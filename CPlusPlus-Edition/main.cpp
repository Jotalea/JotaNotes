#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstdlib>
#include <gtkmm.h>
#include <json/json.h>
#include <openssl/aes.h>
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <openssl/bio.h>
#include <openssl/evp.h>

/*
* sudo apt-get update
* sudo apt-get install libgtkmm-3.0-dev libjsoncpp-dev
* g++ -std=c++11 main.cpp -o jotalea_text_editor `pkg-config gtkmm-3.0 --cflags --libs` -ljsoncpp
* ./jotalea_text_editor
*/

std::string filepath;
Gtk::TextView* txt_edit;
Gtk::Entry* api_key_entry;
Gtk::Entry* endpoint_entry;
Gtk::Entry* char_limit_entry;
Gtk::Entry* ai_model_entry;
Gtk::TextBuffer::iterator start, end;

std::string decrypt_text(const std::string &iv, const std::string &encrypted_text, const std::string &key) {
    AES_KEY aes_key;
    AES_set_decrypt_key(reinterpret_cast<const unsigned char *>(key.c_str()), 256, &aes_key);

    std::string decrypted_text;
    decrypted_text.resize(encrypted_text.size());
    AES_cbc_encrypt(reinterpret_cast<const unsigned char *>(encrypted_text.c_str()), reinterpret_cast<unsigned char *>(&decrypted_text[0]), encrypted_text.size(), &aes_key, reinterpret_cast<unsigned char *>(const_cast<char *>(iv.c_str())), AES_DECRYPT);

    return decrypted_text;
}

std::string open_encrypted_file(const std::string &filepath, const std::string &key) {
    std::ifstream file(filepath, std::ios::in | std::ios::binary);
    if (file) {
        std::string iv, encrypted_text;
        std::getline(file, iv, ':');
        std::getline(file, encrypted_text);

        return decrypt_text(iv, encrypted_text, key);
    }
    return "";
}

std::string encrypt_text(const std::string &text, const std::string &key) {
    std::string iv(AES_BLOCK_SIZE, '\0');
    RAND_bytes(reinterpret_cast<unsigned char *>(&iv[0]), AES_BLOCK_SIZE);

    AES_KEY aes_key;
    AES_set_encrypt_key(reinterpret_cast<const unsigned char *>(key.c_str()), 256, &aes_key);

    std::string encrypted_text;
    encrypted_text.resize(text.size() + AES_BLOCK_SIZE);
    int len = 0;
    AES_cbc_encrypt(reinterpret_cast<const unsigned char *>(text.c_str()), reinterpret_cast<unsigned char *>(&encrypted_text[0]), text.size(), &aes_key, reinterpret_cast<unsigned char *>(&iv[0]), AES_ENCRYPT);

    return iv + encrypted_text;
}

void save_encrypted_file(const std::string &filepath, const std::string &text, const std::string &key) {
    std::string encrypted_text = encrypt_text(text, key);
    std::ofstream file(filepath, std::ios::out | std::ios::binary);
    if (file) {
        file.write(encrypted_text.c_str(), encrypted_text.size());
    }
}

void open_file() {
    Gtk::FileChooserDialog dialog("Please choose a file", Gtk::FILE_CHOOSER_ACTION_OPEN);
    dialog.set_transient_for(*window);
    dialog.add_button("_Cancel", Gtk::RESPONSE_CANCEL);
    dialog.add_button("_Open", Gtk::RESPONSE_OK);

    auto filter_text = Gtk::FileFilter::create();
    filter_text->set_name("Text Files");
    filter_text->add_mime_type("text/plain");
    dialog.add_filter(filter_text);

    auto filter_any = Gtk::FileFilter::create();
    filter_any->set_name("Any files");
    filter_any->add_pattern("*");
    dialog.add_filter(filter_any);

    int result = dialog.run();
    switch (result) {
        case Gtk::RESPONSE_OK: {
            filepath = dialog.get_filename();
            std::ifstream file(filepath);
            if (file) {
                std::string text((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
                txt_edit->get_buffer()->set_text(text);
            }
            break;
        }
        case Gtk::RESPONSE_CANCEL:
            break;
        default:
            break;
    }
}

void new_file() {
    txt_edit->get_buffer()->set_text("");
}

void save_file() {
    Gtk::FileChooserDialog dialog("Please choose a file", Gtk::FILE_CHOOSER_ACTION_SAVE);
    dialog.set_transient_for(*window);
    dialog.add_button("_Cancel", Gtk::RESPONSE_CANCEL);
    dialog.add_button("_Save", Gtk::RESPONSE_OK);

    auto filter_text = Gtk::FileFilter::create();
    filter_text->set_name("Text Files");
    filter_text->add_mime_type("text/plain");
    dialog.add_filter(filter_text);

    auto filter_any = Gtk::FileFilter::create();
    filter_any->set_name("Any files");
    filter_any->add_pattern("*");
    dialog.add_filter(filter_any);

    int result = dialog.run();
    switch (result) {
        case Gtk::RESPONSE_OK: {
            filepath = dialog.get_filename();
            std::ofstream file(filepath);
            if (file) {
                std::string text = txt_edit->get_buffer()->get_text();
                file << text;
            }
            break;
        }
        case Gtk::RESPONSE_CANCEL:
            break;
        default:
            break;
    }
}

void save_file_as() {
    std::string temp_filepath;
    Gtk::FileChooserDialog dialog("Please choose a file", Gtk::FILE_CHOOSER_ACTION_SAVE);
    dialog.set_transient_for(*window);
    dialog.add_button("_Cancel", Gtk::RESPONSE_CANCEL);
    dialog.add_button("_Save", Gtk::RESPONSE_OK);

    auto filter_text = Gtk::FileFilter::create();
    filter_text->set_name("Text Files");
    filter_text->add_mime_type("text/plain");
    dialog.add_filter(filter_text);

    auto filter_any = Gtk::FileFilter::create();
    filter_any->set_name("Any files");
    filter_any->add_pattern("*");
    dialog.add_filter(filter_any);

    int result = dialog.run();
    switch (result) {
        case Gtk::RESPONSE_OK: {
            temp_filepath = dialog.get_filename();
            std::ofstream file(temp_filepath);
            if (file) {
                std::string text = txt_edit->get_buffer()->get_text();
                file << text;
            }
            break;
        }
        case Gtk::RESPONSE_CANCEL:
            break;
        default:
            break;
    }
}

void open_gpt3_window() {
    Gtk::Window* gpt3_win = new Gtk::Window();
    gpt3_win->set_title("Ask ChatGPT");

    Gtk::TextView* user_input = new Gtk::TextView();
    user_input->set_size_request(500, 200);

    Gtk::Button* ask_button = new Gtk::Button("Ask ChatGPT");
    ask_button->signal_clicked().connect(sigc::ptr_fun(&ask_gpt3));

    Gtk::TextView* gpt3_response = new Gtk::TextView();
    gpt3_response->set_size_request(500, 200);
    gpt3_response->set_editable(false);

    Gtk::HBox* hbox = new Gtk::HBox();
    hbox->pack_start(*user_input);
    hbox->pack_start(*ask_button);

    Gtk::VBox* vbox = new Gtk::VBox();
    vbox->pack_start(*hbox);
    vbox->pack_start(*gpt3_response);

    gpt3_win->add(*vbox);
    gpt3_win->show_all_children();
}

void save_config(const Json::Value& config) {
    std::ofstream file("config.json");
    if (file) {
        Json::StreamWriterBuilder builder;
        builder["indentation"] = "    ";
        std::unique_ptr<Json::StreamWriter> writer(builder.newStreamWriter());
        writer->write(config, &file);
    }
}

Json::Value load_config() {
    Json::Value config;
    std::ifstream file("config.json");
    if (file) {
        file >> config;
    }
    return config;
}

void save_api_config() {
    Json::Value config;
    config["api_key"] = api_key_entry->get_text();
    config["endpoint"] = endpoint_entry->get_text();
    config["char_limit"] = char_limit_entry->get_text();
    config["ai_model"] = ai_model_entry->get_text();
    save_config(config);
}

void load_api_config() {
    Json::Value config = load_config();
    api_key_entry->set_text(config.get("api_key", "").asString());
    endpoint_entry->set_text(config.get("endpoint", "https://api.openai.com/v1/chat/completions").asString());
    char_limit_entry->set_text(config.get("char_limit", "512").asString());
    ai_model_entry->set_text(config.get("ai_model", "gpt-3.5-turbo").asString());
}

int main(int argc, char *argv[]) {
    auto app = Gtk::Application::create(argc, argv, "org.gtkmm.example");

    Gtk::Window window;
    window.set_title("Jotalea Text Editor");
    window.set_default_size(640, 360);

    auto vbox = Gtk::manage(new Gtk::VBox());
    window.add(*vbox);

    auto scrolled_window = Gtk::manage(new Gtk::ScrolledWindow());
    scrolled_window->set_policy(Gtk::POLICY_AUTOMATIC, Gtk::POLICY_AUTOMATIC);
    vbox->add(*scrolled_window);

    txt_edit = Gtk::manage(new Gtk::TextView());
    scrolled_window->add(*txt_edit);

    auto menu_bar = Gtk::manage(new Gtk::MenuBar());
    vbox->pack_start(*menu_bar, Gtk::PACK_SHRINK, 0);

    auto menu_file = Gtk::manage(new Gtk::Menu());
    auto menu_item_file = Gtk::manage(new Gtk::MenuItem("_File", true));
    auto menu_file_new = Gtk::manage(new Gtk::MenuItem("_New", true));
    auto menu_file_open = Gtk::manage(new Gtk::MenuItem("_Open", true));
    auto menu_file_save = Gtk::manage(new Gtk::MenuItem("_Save", true));
    auto menu_file_save_as = Gtk::manage(new Gtk::MenuItem("_Save As...", true));
    auto menu_file_exit = Gtk::manage(new Gtk::MenuItem("_Exit", true));

    menu_item_file->set_submenu(*menu_file);
    menu_bar->append(*menu_item_file);

    menu_file->append(*menu_file_new);
    menu_file->append(*menu_file_open);
    menu_file->append(*menu_file_save);
    menu_file->append(*menu_file_save_as);
    menu_file->append(*menu_file_exit);

    menu_file_new->signal_activate().connect(sigc::ptr_fun(&new_file));
    menu_file_open->signal_activate().connect(sigc::ptr_fun(&open_file));
    menu_file_save->signal_activate().connect(sigc::ptr_fun(&save_file));
    menu_file_save_as->signal_activate().connect(sigc::ptr_fun(&save_file_as));
    menu_file_exit->signal_activate().connect(sigc::ptr_fun(&Gtk::Main::quit));

    auto menu_edit = Gtk::manage(new Gtk::Menu());
    auto menu_item_edit = Gtk::manage(new Gtk::MenuItem("_Edit", true));
    auto menu_edit_cut = Gtk::manage(new Gtk::MenuItem("_Cut", true));
    auto menu_edit_copy = Gtk::manage(new Gtk::MenuItem("_Copy", true));
    auto menu_edit_paste = Gtk::manage(new Gtk::MenuItem("_Paste", true));

    menu_item_edit->set_submenu(*menu_edit);
    menu_bar->append(*menu_item_edit);

    menu_edit->append(*menu_edit_cut);
    menu_edit->append(*menu_edit_copy);
    menu_edit->append(*menu_edit_paste);

    menu_edit_cut->signal_activate().connect(sigc::ptr_fun(&Gtk::Clipboard::cut_clipboard, Gtk::Clipboard::get()));
    menu_edit_copy->signal_activate().connect(sigc::ptr_fun(&Gtk::Clipboard::copy_clipboard, Gtk::Clipboard::get()));
    menu_edit_paste->signal_activate().connect(sigc::ptr_fun(&Gtk::Clipboard::paste_clipboard, Gtk::Clipboard::get()));

    auto menu_help = Gtk::manage(new Gtk::Menu());
    auto menu_item_help = Gtk::manage(new Gtk::MenuItem("_Help", true));
    auto menu_help_about = Gtk::manage(new Gtk::MenuItem("_About", true));
    auto menu_help_website = Gtk::manage(new Gtk::MenuItem("_Website", true));

    menu_item_help->set_submenu(*menu_help);
    menu_bar->append(*menu_item_help);

    menu_help->append(*menu_help_about);
    menu_help->append(*menu_help_website);

    menu_help_about->signal_activate().connect(sigc::ptr_fun(&show_help));
    menu_help_website->signal_activate().connect(sigc::ptr_fun(&open_website));

    auto menu_gpt = Gtk::manage(new Gtk::Menu());
    auto menu_item_gpt = Gtk::manage(new Gtk::MenuItem("_ChatGPT", true));
    auto menu_gpt_ask = Gtk::manage(new Gtk::MenuItem("_Ask ChatGPT", true));

    menu_item_gpt->set_submenu(*menu_gpt);
    menu_bar->append(*menu_item_gpt);

    menu_gpt->append(*menu_gpt_ask);

    menu_gpt_ask->signal_activate().connect(sigc::ptr_fun(&open_gpt3_window));

    window.show_all();

    return app->run(window);
}
