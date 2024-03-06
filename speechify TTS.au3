#Region Example
	Global $Stop = False
	HotKeySet('{ESC}', StopConvert) ;Set HotKey = phím ESC để huỷ quá trình convert sang mp3
	Func StopConvert()
		$Stop = True
	EndFunc

	ProgressOn("Progress", "Percent", "Elapsed Time: 0", Default, Default, 16) ;Bật cửa sổ chạy Progress

	$Text = ClipGet() ;Ví dụ chuyển text mà mình đã copy sang Mp3

	$ErrorLogs = _RV_TextToMp3( _
			$Text, _ ;đoạn văn bản cần chuyển đổi
			False, _ ;True = giọng nam, False = giọng nữ
			@DesktopDir & '\tts.mp3', _ ;đường dẫn lưu mp3 về máy tính
			0, _ ; Timeout : thời gian chờ chuyển đổi (tính bằng giây), nếu = 0 thì chờ mãi cho đến khi nhận được phản hồi từ server
			ProgressCallback) ; ProgressCallback sẽ nhận 2 giá trị là Thời gian đã chạy từ khi bắt đầu convert và Phần trăm đã hoàn thành

	If @error Then
		If @error = -1 Then ;khi quá trình convert bị huỷ thì hàm _RV_TextToMp3 sẽ trả về @error = -1
			MsgBox(64 + 0x1000, 'Thông báo', 'Bạn đã huỷ quá trình Convert')
		Else
			MsgBox(64 + 0x1000, 'Lỗi', $ErrorLogs)
		EndIf
	Else
		MsgBox(64 + 0x1000, 'Thông báo', 'Đã chuyển thành công')
	EndIf

	ProgressOff()


	Func ProgressCallback($ElapsedTime, $Percent)
		ProgressSet($Percent, "Elapsed Time: " & Round($ElapsedTime / 1000) & ' s', 'Percent: ' & $Percent & '%')
		;Có thể set điều kiện huỷ quá trình convert Text sang Mp3 trong hàm Callback này bằng cách làm cho nó Return False
		;Ví dụ: If GuiCtrlRead($Checkbox) = $UNCHECK Then Return False
		;hoặc Set HotKey để huỷ như đoạn script ở trên đầu.
		If $Stop = True Then Return False
		;khi quá trình convert bị huỷ thì hàm _RV_TextToMp3 sẽ trả về @error = -1
	EndFunc
#EndRegion
















; #FUNCTION# ====================================================================================================================
; Name...........: _RV_TextToMp3
; Description ...: Chuyển văn bản thành giọng nói tự nhiên
; Syntax.........: _RV_TextToMp3($Text, $Path_Mp3 = '', $Timeout = -1, $ProgressFunction = '')
; Parameters ....:  -	$Text          -	Văn bản cần chuyển
;                         - $Path_Mp3  - Nếu không set đường dẫn thì trả về Binary của Mp3, nếu set thì sẽ ghi ra tệp Mp3
;                         - $Timeout    -  Tính bằng giây. Khi chuyển đổi quá lâu và lớn hơn $Timeout thì huỷ chuyển.
;                         - $ProgressFunction  -  Hàm này sẽ nhận 2 giá trị là Thời gian đã chạy từ khi bắt đầu convert và Phần trăm đã hoàn thành
; Author ........: Chân Thật
; Remarks .......: Sử dụng dịch vụ của speechify.com
; ===============================================================================================================================
Func _RV_TextToMp3($Text, $Voice__Male_True__or__Female_False, $Path_Mp3 = '', $Timeout = -1, $ProgressFunction = '')
	Global $RV_ERRHANDLE = ObjEvent("AutoIt.Error", __RV_ObjErrorHandle)

	# Dồn dòng, phân bổ ngắt quãng câu cho chính xác hơn, sau đó tách văn bản ra nhiều phần cho đủ giới hạn 3000 chữ /1 request
	Local $aText = __RV_TextWrap($Text)
	If @error Then Return SetError(1, 0, Binary(''))
	
	# Số lượng phần đã tách
	Local $q = UBound($aText)
	
	# Gửi các đoạn văn bản đã tách lên speechify.com, ở trạng thái đa luồng
	Local $aSession[$q]
	For $i = 0 To $q - 1
		$aSession[$i] = __RV_Request($aText[$i], $Voice__Male_True__or__Female_False)
		If @error Then
			__RV_SessionEnd($aSession)
			Return SetError(2, $i, Binary(''))
		EndIf
	Next

	# Chờ speechify.com phản hồi kết quả xuất Mp3 ở tất cả các luồng
	$Timeout = Number($Timeout)
	If $Timeout > 0 And $Timeout < 30 Then $Timeout = 30
	$Timeout *= 1000
	Local $Progress = IsFunc($ProgressFunction)
	Local $Success[$q]
	Local $Completed = 0
	Local $TimerInit = TimerInit(), $TimerDiff
	Do
		If $Timeout > 0 And $TimerDiff > $Timeout Then
			__RV_SessionEnd($aSession)
			Return SetError(3, 0, Binary(''))
		EndIf
		For $i = 0 To $q - 1
			If $Success[$i] = True Then ContinueLoop
			$Success[$i] = __RV_WaitConvertMP3($aSession[$i])
			If $Success[$i] = True Then $Completed += 1
		Next
		$TimerDiff = Round(TimerDiff($TimerInit))
		If $Progress And Call($ProgressFunction, $TimerDiff, Round($TimerDiff / 60000 * 100, 2)) == False Then
			__RV_SessionEnd($aSession)
			Return SetError(-1, 0, Binary(''))
		EndIf
		Sleep(100)
	Until $Completed = $q
	If $Progress Then
		Call($ProgressFunction, Round(TimerDiff($TimerInit)), 100)
		Sleep(250)
	EndIf
	
	# Gộp các đoạn Mp3 (ứng với các đoạn văn bản) lại làm một tệp Mp3 hoàn chỉnh
	Local $Ret = Binary(''), $Err = 0
	For $i = 0 To $q - 1
		$Ret &= __RV_Response($aSession[$i])
		$Err += @error
		$aSession[$i] = Null
	Next
	
	# Xuất kết quả
	If IsString($Path_Mp3) And $Path_Mp3 <> '' Then
		__RV_FileWrite($Path_Mp3, $Ret)
		$Ret = Null
		Return SetError($Err, 0, Binary(''))
	Else
		Return SetError($Err, @extended, $Ret)
	EndIf
EndFunc




#Region RV FUNCTIONS
	Func __RV_TextWrap($Text)
		$Text = StringRegExpReplace($Text, '[\x{1680}\x{180E}\x{2000}-\x{205F}\x{3000}]', ' ')
		$Text = StringRegExpReplace($Text, '\R+', @LF)
		;$Text = StringRegExpReplace($Text, '([\?\!])\h*?"', '$1.')
		;$Text = StringRegExpReplace($Text, '["\.]\h*?([\r\n])', '?$1')
		;$Text = StringRegExpReplace($Text, '[\!\?]\h*?[\!\?]', '?.')
		$Text = StringRegExpReplace($Text, '\.{4,}', '...')
		;$Text = StringRegExpReplace($Text, '\.{3}', '?.')
		;$Text = StringRegExpReplace($Text, '\.{2}', '.')
		;$Text = StringRegExpReplace($Text, '(?m)^[\h\*]+$[\r\n]?', '')
		;$Text = StringRegExpReplace($Text, '(*UCP)(\w)\h*?([\r\n])', '$1 ?.$2')
		;$Text = StringRegExpReplace($Text, ':', '?')
		$Text = StringRegExpReplace($Text, '(\d+,)\. (\d+)', '$1$2')
		Local $aText = StringRegExp($Text, '(?m)(.{1,2999}(?:\+|$))', 3)
		$Text = ''
		Return SetError(@error, @extended, $aText)
	EndFunc

	Func __RV_Request($sEncodedText, $Voice__Male_True__or__Female_False)
		Local $Session = ObjCreate('WinHttp.WinHttpRequest.5.1')
		If Not IsObj($Session) Then Return SetError(-1, @extended, $Session)
		With $Session
			.Open('POST', 'https://audio.api.speechify.com/generateAudioFiles', True) ;ASYNC
			.SetRequestHeader('Content-Type', 'application/json')
			.Send('{' & _
					'"audioFormat":"mp3",' & _
					'"paragraphChunks":["' & __RV_TextEncode($sEncodedText) & '"],' & _
					'"voiceParams":' & _
					'{' & _
					'"name":"' & ($Voice__Male_True__or__Female_False ? 'namminh' : 'hoaimy') & '",' & _
					'"engine":"azure",' & _
					'"languageCode":"vi-VN"' & _
					'}' & _
					'}')
		EndWith
		Return SetError(@error, @extended, $Session)
	EndFunc

	Func __RV_WaitConvertMP3($Session)
		With $Session
			Return Execute('.WaitForResponse(0)')
		EndWith
	EndFunc

	Func __RV_Response($Session)
		With $Session
			If Execute('.WaitForResponse(0)') = False Then Return SetError(1, 0, Binary(''))
			Local $res = BinaryToString(Execute('.ResponseBody'))
		EndWith
		Local $b64_Mp3Chunk = StringRegExp($res, '"audioStream":"([^"]+)"', 1)
		If @error Or $b64_Mp3Chunk[0] = '' Then Return SetError(2, 0, Binary(''))
		Local $bin_Mp3 = __RV_B64Decode($b64_Mp3Chunk[0])
		If @error Or $bin_Mp3 = '' Then Return SetError(3, 0, Binary(''))
		Return $bin_Mp3
	EndFunc

	Func __RV_SessionEnd(ByRef $aSession)
		For $idx = 0 To UBound($aSession) - 1
			$aSession[$idx] = Null
		Next
	EndFunc
	
	Func __RV_FileWrite($Path, $Data)
		Local $hFile = FileOpen($Path, 2 + 8 + 16)
		FileWrite($hFile, $Data)
		FileClose($hFile)
	EndFunc
	
	Func __RV_ObjErrorHandle()
		Return SetError(1, 0, '')
	EndFunc
	
	Func __RV_TextEncode($sData)
		If $sData == '' Then Return ''
		Local $sResult = Call('Execute', '"' & StringReplace(StringRegExpReplace($sData, '([^\w\-\.\~\h])', '" & "\\u" & ' & 'Hex(AscW("${1}"), 4) & "'), 'AscW(""")', 'AscW("""")', 0, 1) & '"')
		If $sResult == '' Then Return SetError(1, 0, $sData)
		Return $sResult
	EndFunc
	
	Func __RV_B64Decode($base64Data)
		If $base64Data == '' Then Return SetError(1, 0, '')
		Local $tStruct = DllStructCreate("int")
		Local $a_Call = DllCall("Crypt32.dll", "int", "CryptStringToBinary", "str", $base64Data, "int", 0, "int", 1, "ptr", 0, "ptr", DllStructGetPtr($tStruct, 1), "ptr", 0, "ptr", 0)
		If @error Or Not $a_Call[0] Then Return SetError(2, 0, '')
		Local $tsByte = DllStructCreate("byte[" & DllStructGetData($tStruct, 1) & "]")
		$a_Call = DllCall("Crypt32.dll", "int", "CryptStringToBinary", "str", $base64Data, "int", 0, "int", 1, "ptr", DllStructGetPtr($tsByte), "ptr", DllStructGetPtr($tStruct, 1), "ptr", 0, "ptr", 0)
		If @error Or Not $a_Call[0] Then Return SetError(3, 0, '')
		Local $binaryData = DllStructGetData($tsByte, 1)
		Return $binaryData
	EndFunc
#EndRegion
