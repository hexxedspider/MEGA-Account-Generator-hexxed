<h1 align="center">
  <img src="./img/readme-icon.png" alt="Discord OAuth" width="512">
  <br>
  MEGA.nz Account Creator
</h1>

<h4 align="center">An Open Source demonstration of creating / managing multiple  <a href="https://mega.nz" target="_blank">MEGA.nz</a> accounts.</h4>

<h6 align="center">I have no affiliation with MEGA.nz, and this is not an official MEGA.nz product. You are solely responsible what you do.</h6>

<br>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#acknowledgements">Acknowledgements</a> •
  <a href="#support">Support</a> •
  <a href="#license">License</a>
</p>
<div align="center">
  <img src="./img/demo.png" alt="Discord OAuth Demo" width="800px" style="border-radius:7px;">
</div>

<br>

## Key Features

* Generate new MEGA.nz accounts in bulk.
* Automatically verify emails.
* **Check storage usage** for all accounts and display total storage.
* **Automated weekly login scheduler** to keep accounts alive.
* **Tag/organize accounts** with customizable purposes.
* Keep accounts alive by logging in periodically.
* Sift through accounts and copy email, password, or both to clipboard.

<br>

## How To Use

**Prerequisites:**
* [megatools](https://megatools.megous.com/) installed and added to your PATH
* Python 3.6+

**Installation:**
```bash
git clone https://github.com/hexxedspider/MEGA-Account-Generator.git
cd MEGA-Account-Generator
pip install -r requirements.txt
```

**Usage:**
```bash
python generate_accounts.py
python signin_accounts.py
python check_storage.py
python manage_tags.py
python account_selector.py
```

<details><summary>Click here for Advanced Usage</summary>

```bash
python generate_accounts.py [-h] [-n NUMBER_OF_ACCOUNTS] [-t NUMBER_OF_THREADS] [-p PASSWORD]
python signin_accounts.py
python check_storage.py
python setup_scheduler.py [--remove]
python manage_tags.py
python account_selector.py
```

**generate_accounts.py**:
- `-n` Number of new accounts to generate. Default: 3 accounts.
- `-t` Number of threads for concurrent account creation. Maximum: 8.
- `-p` Password to use for all accounts. Default: random password per account.
- `-h` Show help.

**signin_accounts.py**: Log into all accounts to keep them alive and prevent deletion.

**check_storage.py**: Check storage usage for all accounts, display total storage across all accounts, and update CSV with usage data.

**setup_scheduler.py**: Set up a Windows scheduled task to automatically run `signin_accounts.py` weekly. Use `--remove` flag to uninstall the scheduled task.

**manage_tags.py**: Interactive CLI to tag/organize accounts by purpose. Tag accounts, filter by purpose, and view grouped accounts.

**account_selector.py**: Browse accounts and copy email, password, or both (email:password format) to clipboard. Shows account metadata including purpose and storage usage.

</details>

<br>

## FAQ

- Will this automatically verify emails?
  - Yes, the script will automatically fetch the verification link from the email, and use it to verify the account.

- Can I log in to the accounts, on the web, after generating them?
  - Yes, that is how this script is intended to be used. Simply copy the email address and password from the CSV file and log in to the account.

- There are multiple passwords in the CSV file. Which one should I use?
  - As of May 2024, all columns have appropriate headers.
  - You will need to use the password in the second columns titled `MEGA Password`.

- What's with the other password then? And why do I need the `Mail.tm ID`?
  - The other password, in the `Mail.tm Password` column, is the password for the Mail.tm account.
  - You can use this password to sign in to the temporary Mail.tm account on their website.
  - In order to access the Mail.tm account, through their API, we also need the ID of the account. This is stored in the case it will be needed in the future.

- What's with the `-p`/`--password` flag? Do I need it?
  - The `-p` flag is optional.
  - You can use this to specify a password for all accounts. If not specified, a random password will be generated for each account.

- Can I generate multiple accounts in parallel?
  - Yes, this script can generate multiple accounts in parallel using the `-t` flag.
  - This is, however, not recommended, and will likely result in rate limits from Mail.tm.
  - The script will automatically retry in the event of a rate limit up to 5 times.

- Why can I only run 8 threads?
  - Because of rate limits from Mail.tm.
  - We do not want to overload their service, which they generously offer for free.

- Something is broken? I'm having trouble using this script.
  - Please [open an issue on GitHub](https://github.com/hexxedspider/MEGA-Account-Generator/issues). Be sure to include information and screenshots.

<br>

## Acknowledgements

This software was based heavily on [IceWreck/MegaScripts](https://github.com/IceWreck/MegaScripts).<br>
His original Python script utilized [GuerillaMail](https://www.guerrillamail.com/GuerrillaMailAPI.html) to generate temporary email addresses.<br>
I've modified the script to use [Mail.tm](https://api.mail.tm/) instead, with a lot of help from [qtchaos/py_mega_account_generator](https://github.com/qtchaos/py_mega_account_generator).<br>
I highly recommend checking out both of their projects.<br><br>
This script was forked from f-o, so majority of the code is from them.


## Support
The original script was created by [f-o](https://github.com/f-o), and I only forked and added to it.<br>
If you find it useful, please consider supporting Fox by donating below.
<br><br>
<a href="https://www.buymeacoffee.com/foxdk" target="_blank"><img src="./img/bmc-button.png" alt="Buy Me A Coffee" width="160"></a>

<br>

## License

[MIT License](https://mit-license.org/)
```
Copyright (c) 2023 Fox

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> [@hexxedspider](https://github.com/hexxedspider) &nbsp;·&nbsp;
> [@f-o](https://github.com/f-o)