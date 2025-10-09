# CIPHER

Yeah so I made a chat thing cause why not. It's called CIPHER and it lets you chat with people over the internet or whatever.

## What is this

Encrypted chat server/client thing I threw together. You can host a server and your friends can connect to it and chat. Pretty simple really.

Features I guess:
- Encryption (PBKDF2 + Fernet, sounds fancy right?)
- Typing indicators so you know when someone's typing
- Commands like /whisper for DMs and stuff
- Works on Windows and Linux (probably Mac too idk)
- Tunneling support with bore so you can chat with people outside your network
- Logs everything to a file cause why not
- Interactive menus with arrow keys (looks cool)

## How it works

Ok so basically it's like this:

```
   YOU (client)                    SERVER                    FRIEND (client)
        |                             |                             |
        | [1] connect to server       |                             |
        |---------------------------->|                             |
        |                             |                             |
        | [2] "what's ur name?"       |                             |
        |<----------------------------|                             |
        |                             |                             |
        | [3] "im bob"                |                             |
        |---------------------------->|                             |
        |                             | [4] "bob joined"            |
        |                             |---------------------------->|
        |                             |                             |
        | [5] type message            |                             |
        |---------------------------->|                             |
        |                             | [6] broadcast msg           |
        |                             |---------------------------->|
        | [7] get message back        |                             |
        |<----------------------------|                             |
```

The encryption part:
```
your message: "hello"
     |
     v
[encrypt with fernet] --> "gAAAAABh..." (encrypted)
     |
     v
[send over network] --> server gets it
     |
     v
[decrypt on server] --> "hello" (readable)
     |
     v
[encrypt again] --> "gAAAAABh..."
     |
     v
[send to other clients] --> they decrypt it
```

## Setup

1. Install Python
2. Run the program and it'll auto install the packages (cryptography, colorist), or if you're cool just do `pip install cryptography colorist`
3. That's it lol

## How to use

### Hosting a server

Just run `python cipher.py` and pick "Host cipher server"

You got 2 options:
- **Local hosting** - only works on same wifi/network
- **Host with bore** - uses bore tunnel so anyone on the internet can connect
  - You need bore for this: https://github.com/ekzhang/bore/releases
  - Just drop bore.exe in the same folder as cipher.py

When you host with bore it'll give you a url like `bore.pub:12345` - send that to your friends

### Connecting to a server

1. Pick "Connect to server"
2. Enter the IP/URL
   - If local: use the host's local IP
   - If bore: use the bore.pub url they gave you
3. Enter the port (default is 8052)
4. Pick a username
5. Start chatting

### Commands

```
/quit          - disconnect (use this don't just close the window)
/users         - see who's online
/whisper       - DM someone (/whisper username message)
/clear         - clear your screen
/help          - shows commands
```

## Network diagram

```
                      INTERNET
                         |
                         |
       ┌─────────────────┼─────────────────┐
        |                |                 |
        v                v                 v
   [Client A]       [Server]          [Client B]
  (your friend)   (your computer)        (you)
        |                |                 |
        |  encrypted msg |                 |
        |--------------->|                 |
        |                | encrypted msg   |
        |                |--------------->|
        |                |                 |
        |  typing signal |                 |
        |--------------->| typing signal   |
        |                |--------------->|
        |                |                 |

with bore tunnel:
   [Client A] <---> bore.pub <---> [Your Server] <---> [Client B]
  (internet)       (tunnel)      (your computer)     (your network)
```

## Settings

In the settings menu you can change:
- Port (default 8052)
- Max clients (default 10)
- Encryption on/off (keep it on)
- Tor service info (doesn't do anything yet lol)
- Tunneling info display

## The encryption stuff

Uses PBKDF2-HMAC-SHA256 with 100k iterations to derive a key from a password, then Fernet for actual encryption.

Yeah I know the password is hardcoded to "change_this" but whatever, change it if you want. Same salt too. This isn't Fort Knox it's just a chat app.

```
password: "change_this"
     |
     v
[pbkdf2 + salt] --> 32 byte key
     |
     v
[base64 encode] --> fernet key
     |
     v
[fernet cipher] --> encrypt/decrypt messages
```

## File structure

```
cipher.py              # the main program (this does everything)
chat_history_log       # logs all messages (created automatically)
bore.exe               # optional - for tunneling
```

## Troubleshooting

**Can't connect to server**
- Make sure server is running
- Check firewall isn't blocking the port
- If using bore make sure the url is right

**Encryption errors**
- Make sure both client and server have same encryption settings
- If you changed the password/salt, change it on both sides

**Typing indicators weird**
- Yeah sometimes they glitch idk why
- Still works for chatting tho

**Bore not working**
- Did you download it?
- Is it in the same folder?
- Maybe try running it manually first: `bore local 8052 --to bore.pub`

## Stuff I might add later

- [ ] File sending
- [ ] Actual tor support (not just a toggle that does nothing)
- [ ] More tunnel options (cloudflare, ngrok, etc)
- [ ] Custom colors
- [ ] Message history when you join
- [ ] Better error handling probably

## Notes

- Don't use this for anything serious lmao it's just a fun project
- The code is messy I know, don't judge me
- Logs are stored in plain text so don't say anything sus
- If you find bugs cool let me know or whatever
- The ascii art is sick tho right?

## License

Idk do whatever you want with it, just don't sell it or claim you made it

---

Made by me cause I was bored. If you use this say hi or something

Also if you're reading this far into the readme you're probably cool
