rs:
	pyside6-rcc resource.qrc -o resource.py

bd:
	rm -rf E:/Project/Python/_APP/autosub/.build_app/obfdist
	rm -rf E:/Project/Python/_APP/autosub/.build_app/src
	mkdir E:/Project/Python/_APP/autosub/.build_app/src
	cp -r E:/Project/Python/ReviewPhim/gui E:\Project\Python\_APP\autosub\.build_app\src
	cp -r E:/Project/Python/ReviewPhim/flv_con E:\Project\Python\_APP\autosub\.build_app\src
	#cp -r E:/Project/Python/ReviewPhim/qt_core.py E:\Project\Python\_APP\autosub\.build_app\src
	cp -r E:/Project/Python/ReviewPhim/NTSAutoSub.py E:\Project\Python\_APP\autosub\.build_app\src
	cp -r E:/Project/Python/ReviewPhim/NTSAutosub.spec E:\Project\Python\_APP\autosub\.build_app\src
	#rm -rf E:/Project/Python/_APP/autosub/.build_app/build
	#rm -rf E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	#pyarmor gen -O E:\Project\Python\_APP\autosub\.build_app\obfdist --enable-rft --mix-str --enable-jit --obf-code 2 --assert-call --assert-import -r E:\Project\Python\_APP\autosub\.build_app\src\flv_con
	pyarmor gen -O E:\Project\Python\_APP\autosub\.build_app\obfdist --enable-rft --mix-str --enable-jit --obf-code 2 --assert-call -r E:\Project\Python\_APP\autosub\.build_app\src\gui
	pyarmor gen -O E:\Project\Python\_APP\autosub\.build_app\obfdist --enable-rft --mix-str --enable-jit --obf-code 2 --assert-call --assert-import NTSAutoSub.py
	pyarmor gen -O E:\Project\Python\_APP\autosub\.build_app\obfdist --enable-rft --mix-str --enable-jit --obf-code 2 --assert-call --assert-import gui
	#pyarmor gen --pack  E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub\NTSAutoSub.exe -r NTSAutoSub.py flv_con gui
	#pyarmor cfg rft_excludes "QtGui"
	#pyarmor gen  --pack E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub\NTSAutoSub.exe --enable-rft --mix-str --enable-jit --obf-code 2 --assert-call --assert-import -r ffsub
	pyinstaller NTSAutosub.spec --noconfirm
#	cp -r E:\Project\Python\_APP\autosub/audio E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/db E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/font E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:/Project/Python/ReviewPhim/images E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:/Project/Python/ReviewPhim/model E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/logs E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/output E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/profile E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/storage E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/temp E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/theme E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/video E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/voice E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/_str.dll E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/7z.dll E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/7z.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:/Project/Python/ReviewPhim/ffmpeg.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:/Project/Python/ReviewPhim/ffplay.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:/Project/Python/ReviewPhim/ffprobe.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/update.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/MediaInfo.dll E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/MediaInfo.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/rubberband.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
#	cp -r E:\Project\Python\_APP\autosub/sndfile.dll E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub

	#python -m nuitka --disable-console --onefile --mingw64 --remove-output  --include-package-data=_soundfile_data --include-package-data=tls_client --include-package-data=undetected_chromedriver --include-package-data=seleniumwire --include-package-data=budoux --include-package-data=qt_material --include-package-data=wordsegment --enable-plugin=pyside6 --include-qt-plugins=all --output-dir=E:/Project/Python/_APP/autosub --follow-imports --noinclude-pytest-mode=nofollow --noinclude-setuptools-mode=nofollow --nofollow-import-to=tkinter --noinclude-unittest-mode=nofollow --windows-icon-from-ico=icon.ico NTSAutoSub.py

bdc:
	#pyarmor pack -e " -w -F --icon=icon.ico" main.py --standalone --force-stdout-spec='%PROGRAM_BASE%.out.txt' --encrypt-stderr --force-stderr-spec='%PROGRAM_BASE%.err.txt' --enable-plugin=traceback-encryption
	python -m nuitka --no-deployment-flag=self-execution --onefile --msvc=14.3 --enable-plugin=data-hiding --enable-plugin=anti-debugger  --remove-output --noinclude-numba-mode=nofollow --include-data-files=E:/Project/Python/ReviewPhim/libsndfile.dll=.  --include-package-data=budoux --include-package-data=tls_client --include-package-data=undetected_chromedriver --include-package-data=seleniumwire --include-package-data=qt_material --include-package-data=wordsegment --enable-plugin=pyside6 --include-qt-plugins=all --output-dir=E:/Project/Python/_APP/autosub  --follow-imports --noinclude-pytest-mode=nofollow --noinclude-setuptools-mode=nofollow --nofollow-import-to=tkinter --noinclude-unittest-mode=nofollow --windows-icon-from-ico=icon.ico NTSAutoSub.py

py:
	pyinstaller --noconfirm --onefile --console --icon "D:/Project/Python/ReviewPhim/icon.ico" --add-data "D:/Project/Python/ReviewPhim/dist/db;db/" --add-data "D:/Project/Python/ReviewPhim/dist/frames;frames/" --add-data "D:/Project/Python/ReviewPhim/dist/images;images/" --add-data "D:/Project/Python/ReviewPhim/dist/output;output/" --add-data "D:/Project/Python/ReviewPhim/dist/temp;temp/" --add-data "D:/Project/Python/ReviewPhim/dist/custom.css;." --add-data "D:/Project/Python/ReviewPhim/dist/my_theme.xml;." --add-data "D:/Project/Python/ReviewPhim/dist/ffmpeg.exe;." --add-data "D:/Project/Python/ReviewPhim/dist/ffsub.exe;." --add-data "D:/Project/Python/ReviewPhim/dist/update.exe;."  "D:/Project/Python/ReviewPhim/NTSAutoSub.py"
	#pyinstaller --noconfirm --onefile --console --icon "D:/Project/Python/ReviewPhim/icon.ico" --add-data "output;output/" "output.py"
copy:
	cp -r E:\Project\Python\_APP\autosub/audio E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/db E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/font E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:/Project/Python/ReviewPhim/images E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:/Project/Python/ReviewPhim/model E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/logs E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/output E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/profile E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/storage E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/temp E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/theme E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/video E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/voice E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/_str.dll E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/7z.dll E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/7z.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:/Project/Python/ReviewPhim/ffmpeg.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:/Project/Python/ReviewPhim/ffplay.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:/Project/Python/ReviewPhim/ffprobe.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/update.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/MediaInfo.dll E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/MediaInfo.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/rubberband.exe E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub
	cp -r E:\Project\Python\_APP\autosub/sndfile.dll E:\Project\Python\_APP\autosub\.build_app\NTSAutoSub

git:
	git add .
	git commit -m "up"
	git push