## ndl_downloader

This is a python script for downloading books automatically from the Japanese National Diet Library.

You can either download the books in high quality jpgs or slightly lower quality pdfs.

Please note that sending too many requests to the library's server at once will both slow the server down and get your IP blocked temporarily. For this reason, I have added a timer to wait between downloads. Please be considerate and do not set the time interval too low.

The following libraries are required to use this script: [bs4] (https://www.crummy.com/software/BeautifulSoup/), [PyPDF] (http://mstamy2.github.io/PyPDF2/), [requests] (http://docs.python-requests.org/en/master/), and [regex] (https://bitbucket.org/mrabarnett/mrab-regex).

When using this script in Windows, depending on your system locale, you may experience encoding errors in command prompt. This is a Windows problem and there is nothing that can be done to fix it in the code. To work around this issue, try changing the code table of command prompt to Unicode by using the following command: `chcp 65001`.

2022.06.04 Update

Added a combination of an AutoHotkey (ndl-screens.ahk) and python (bordercrop.py) script to download books which are only viewable in browser.

The following libraries are required to use the python script: [opencv] (https://pypi.org/project/opencv-python/), [NumPy] (https://numpy.org/).

In order to use the script, first activate ndl-screens.adk. Then open the book you wish to capture in your browser to the first page that you wish to capture. Set your browser to fullscreen mode (F11 in Chrome), then click the fullscreen option on the NDL viewer toolbar. You are now ready to start capturing screenshots. Be sure that all popups are disabled before running the script, as everything viewable on the screen other than your cursor will be captured in the screenshots. Next, press the defined hotkey (default setting: Ctrl+F10) to start the script. You will be asked to enter the total number of pages in the book and the page number that you wish to start from (both can be checked from the toolbar). Be sure that the toolbar has fully disappeared before clicking okay to the second prompt. You can stop the script at any time by pressing the defined hotkey again.

Note that it is highly recommended to use a high resolution monitor (or some sort of super resolution option if you have the required graphics card: Google "Nvidia Dynamic Super Resolution" or "AMD Super Virtual Resolution") when taking screenshots. While this script should work for any resolution, lower resolutions, such as 1080p, usually result in blurry or unreadable text. From personal testing, 4K seems to be the sweet spot. Resolutions above 4K (I have personally tested up to 8K) seem to provide little to no improvement in image quality, while greatly increasing file size.

Also note that while NDL allows for taking screenshot of all publically available materials, they strictly prohibit sharing such screenshots with others or posting them to social media. Please respect these restrictions when taking screenshots as NDL really has gone above and beyond their duty in providing this vast wealth of materials to the general public. For more details, please see the FAQs below.
https://www.ndl.go.jp/jp/help/service_digi_individuals.html

Pro tip: For books that have the page-turning arrows overlapping with the page images, you can disable the arrows using Developer Tools (Ctrl+Shift+I in Chrome) and the script will still work just fine!
