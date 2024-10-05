import tkinter as tk
from tkinter import ttk
from opensearchpy import OpenSearch
import certifi

# OpenSearch client configuration
client = OpenSearch(
    hosts=['http://192.168.0.111:9200'],
    http_auth=('your-username', 'your-password'),
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
    ca_certs=certifi.where()
)

def search(event=None):
    query = search_var.get()
    if query:
        try:
            response = client.search(
                index='interns',
                body={
                    'query': {
                        'multi_match': {
                            'query': query,
                            'fields': ['JOB_TITLE', 'JOB_CONTENT_TEXT'],
                            'type': 'phrase_prefix'
                        }
                    },
                    'size': 10
                }
            )
            
            results_list.delete(0, tk.END)
            for hit in response['hits']['hits']:
                results_list.insert(tk.END, hit['_source']['JOB_TITLE'])
        except Exception as e:
            print(f"Error: {e}")
    else:
        results_list.delete(0, tk.END)

# Create main window
root = tk.Tk()
root.title("OpenSearch Search-as-you-type")
root.geometry("400x500")

# Create and place widgets
search_var = tk.StringVar()
search_var.trace("w", lambda name, index, mode: search())

search_entry = ttk.Entry(root, textvariable=search_var, width=50)
search_entry.pack(pady=10)

results_list = tk.Listbox(root, width=50, height=20)
results_list.pack(pady=10)

# Start the GUI event loop
root.mainloop()