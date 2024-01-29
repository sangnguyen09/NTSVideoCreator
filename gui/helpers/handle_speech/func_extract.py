from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
# yt-dlp --write-auto-sub --write-sub --sub-lang zh-Hans --convert-subs srt -o "E:\Project\Python\TTSfree\test_en_ch" --skip-download --ignore-errors J3nQPCJDhV0


def get_srt_youtube (id_video, langgude, filename):
	try:
		transcript_list = YouTubeTranscriptApi.list_transcripts(id_video)
		transcript = transcript_list.find_transcript([langgude])
		format = SRTFormatter()
		data = format.format_transcript(transcript.fetch())
		
		with open(filename, 'w', encoding='utf-8') as json_file:
			json_file.write(data)
		
		return True
	except:
		return False
	
# def get_srt
if __name__ == '__main__':
	get_srt_youtube()
