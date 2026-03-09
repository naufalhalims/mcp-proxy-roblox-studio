import sys
import json
import subprocess
import threading

# Jalur ke eksekutor MCP Roblox Studio Anda (ubah sesuai dengan lokasi instalasi)
TARGET_EXE = "StudioMCP.exe"

def forward_stdin(process):
    for line in sys.stdin:
        process.stdin.write(line)
        process.stdin.flush()

def main():
    # Menjalankan StudioMCP asli
    process = subprocess.Popen(
        [TARGET_EXE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        text=True,
        bufsize=1,
        encoding='utf-8'
    )

    # Meneruskan perintah dari Antigravity ke Roblox
    t = threading.Thread(target=forward_stdin, args=(process,), daemon=True)
    t.start()

    # Mencegat output dari Roblox ke Antigravity
    for line in process.stdout:
        try:
            msg = json.loads(line)
            
            # Mencari skema alat (tools) yang dikirim Roblox
            if msg.get("result") and "tools" in msg["result"]:
                for tool in msg["result"]["tools"]:
                    if "inputSchema" in tool and "properties" in tool["inputSchema"]:
                        props = tool["inputSchema"]["properties"]
                        
                        # Memperbaiki bug key_code untuk Gemini
                        if "key_code" in props:
                            if "enum" in props["key_code"]:
                                del props["key_code"]["enum"]
                            props["key_code"]["type"] = "string"
            
            # Mengirim kembali JSON yang sudah bersih ke Gemini
            sys.stdout.write(json.dumps(msg) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError:
            sys.stdout.write(line)
            sys.stdout.flush()

if __name__ == "__main__":
    main()