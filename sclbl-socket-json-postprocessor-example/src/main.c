// Standard system includes
#include <stdio.h>
#include <signal.h>

// Local includes
#include "yyjson.h"
#include "sclbl_socket_utils.h"

// Flag to keep track of interrupts
volatile sig_atomic_t interrupt_flag = false;

// Function forward declarations
void printJSONDocument(yyjson_doc *input_document);
void handle_interrupt(int sig);

int main(int argc, char *argv[])
{
    // Get rid of compilation warnings
    if (argc != 2)
    {
        printf("EXAMPLE POSTPROCESSOR: Started with incorrect command line arguments.\n");
        exit(2);
    }

    // Set signal handler to listen for interrupt signals
    signal(SIGINT, handle_interrupt);

    const char *socket_path = argv[1];

    printf("EXAMPLE POSTPROCESSOR: Starting up with socket path: %s.\n", socket_path);

    char *input_buffer = NULL;
    size_t allocated_buffer_size = 0;
    uint32_t message_length;

    int socket_fd = sclbl_socket_create_listener(socket_path);

    // While no interrupt signal received
    while (interrupt_flag == false)
    {
        int connection_fd = sclbl_socket_await_message(socket_fd, &allocated_buffer_size, &input_buffer, &message_length);

        if (connection_fd == -1)
        {
            // Connection timed out, continue to wait for message again.
            // Useful to test if program should terminate and break
            continue;
        }

        yyjson_doc *input_doc = yyjson_read(input_buffer, (size_t)message_length, 0);

        printJSONDocument(input_doc);

        sclbl_socket_send_to_socket(connection_fd, input_buffer, message_length);
    }

    printf("EXAMPLE POSTPROCESSOR: Exiting.\n");
}

void printJSONDocument(yyjson_doc *input_document)
{
    yyjson_val *document_root = yyjson_doc_get_root(input_document);

    yyjson_val *output_object = yyjson_obj_get(document_root, "output");

    printf("EXAMPLE POSTPROCESSOR: Received document output object has keys:\n");

    size_t idx, max;
    yyjson_val *key, *val;
    yyjson_obj_foreach(output_object, idx, max, key, val)
    {
        printf("EXAMPLE POSTPROCESSOR: %s\n", yyjson_get_str(key));
    }
}

void handle_interrupt(int sig)
{
    interrupt_flag = true;
}
