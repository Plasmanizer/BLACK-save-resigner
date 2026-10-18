## Warning
It is made and written with Claude. Intended for personal use, it comes with no warranty or support. Back up your saves first before using this script.

Also, the rest of the documentation below are **Fully** AI Generated. So keep that in mind, and i only tested it on my Arch Linux system. I'll revise the documentation by hand later.

# blackresign.py

Makes original Xbox saves for **Black** (2006) load in [BLACK-XBERecomp](https://github.com/TGP482/BLACK-XBERecomp), the PC port.

If the port says the **profile is damaged** after you copy a save from a real Xbox, the save is usually fine. Its signature is just wrong for the port. This script fixes the signature and changes nothing else.

## Requirements

Python 3.6 or newer. Nothing else to install.

## Usage

```
python3 blackresign.py save_folder          # copies it to save_folder_resigned and fixes every Profile
python3 blackresign.py Profile              # fixes one file, writes Profile.resigned
python3 blackresign.py --inplace Profile    # overwrites the file and keeps Profile.bak
python3 blackresign.py --check Profile      # only tells you if the signature is valid
```

On Windows, use `python` or `py` instead of `python3`.

The original is never changed, except with `--inplace`, which makes a `.bak` copy first.

## Using a save

1. Copy the save folder off the Xbox. It is in `E:\UDATA\45410083\<save id>\`.
2. Run `python3 blackresign.py <save id>`.
3. Back up `hdd/E/UDATA/45410083/` next to `BLACK.exe`.
4. Copy the `<save id>_resigned` folder into `hdd/E/UDATA/45410083/`.
5. Start the game and open the load menu.

Europe saves work the same way and go in the same `45410083` folder.

## If it still says damaged

- Run `--check` on the `Profile` the port is using. If it says "NOT valid", the wrong file was copied.
- If it says "valid" and the game still complains, the save has a wrong internal checksum, for example from another tool that edited it. This script can't fix that. Use the C++ `blackresign` program or its GUI.

## Limitation

- It only re-signs `Profile` files of exactly 6144 bytes. It does not rename profiles.
- Tested on two saves from the [GameFAQs Black saves page](https://gamefaqs.gamespot.com/xbox/920901-black/saves) (North America by demon_eyes_kiru, Europe by GrindieBrain). These are Action Replay saves from real consoles and may have been edited before upload.

## How it works

The last 20 bytes of `Profile` are `HMAC-SHA1(key, HMAC-SHA1(key, first 6124 bytes))`. The port uses 16 zero bytes as the key. The script recomputes those 20 bytes.

## License

GPL-3.0. See `LICENSE`.
