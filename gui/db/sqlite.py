import json

from peewee import TextField, SqliteDatabase, Model, CharField

from gui.helpers.constants import JOIN_PATH, PATH_DB

# from playhouse.apsw_ext import CharField, Model

apsw_db = SqliteDatabase(JOIN_PATH(PATH_DB,'app.db'))


class BaseModel(Model):
	class Meta:
		database = apsw_db


class CauHinhTuyChonModel(BaseModel):
	ten_cau_hinh = CharField(unique=True, default="default")
	value = TextField(default=json.dumps({
		"use_gpu": False,
		"remember_me": False,
		"dich_tu_dong":False,
		"remove_sound":False,
		"src_output": "",
		"src_graphics_config": "",
		
		"sub_hien_thi": "translate",
		
		"vi_tri_sub_dich": 6,
		"style_sub_dich": False,
		"add_mau_sub_dich": False,
		"mau_sub_dich": "#ffffff",
		"opacity_mau_sub_dich": 100,
		"vien_sub_dich": False,
		"mau_vien_sub_dich": "#000000",
		"do_day_vien_sub_dich": "1px",
		"nen_sub_dich": False,
		"mau_nen_sub_dich": "#000000",
		"opacity_nen_sub_dich": 80,
		"font_sub_dich": False,
		"font_family_sub_dich": "Arial",
		"font_size_sub_dich": "12px",
		
		"vi_tri_sub": 2,
		"style_sub": False,
		"add_mau_sub": False,
		"mau_sub": "#ffffff",
		"opacity_mau_sub": 100,
		"vien_sub": False,
		"mau_vien_sub": "#000000",
		"do_day_vien_sub": "1px",
		"nen_sub": False,
		"mau_nen_sub": "#000000",
		"opacity_nen_sub": 80,
		"font_sub": False,
		"font_family": "Arial",
		"font_size": "12px",
		
		# "use_proxy": False,
		"proxy_raw": '',
		"tmproxy": '',
		"network_actived": "wifi",
		
		# "dich_sub": False,
		
		"tab_translate_active": 0,
		# "ngon_ngu_dich": "vi",
		# "ngon_ngu_goc": "en",
		"servers_trans": {
			"destination_language": "vi",
			# "source_language":"en",
			"apikey": "",
		},
		
		"text_to_speech": False,
		"servers_tts": {
			"type_tts_sub": "origin",
			"gender": "female",
			"language_tts": "vi",
			"speed": 100,
			"apikey": "",
			"mode": "v1",
			"pitch": 0,
		},
		"tab_tts_active": 0,
		
		"trang_thai_cau_hinh_render": False,
		"che_sub_cu": False,
		"them_nhac": False,
		"them_nhac_co_dinh": False,
		"src_nhac_co_dinh": "",
		"them_nhac_ngau_nhien": False,
		"src_nhac_ngau_nhien": "",
		"am_luong_nhac_nen": 50,
		"them_intro_outro": False,
		"them_intro": False,
		"src_intro": "",
		"them_outro": False,
		"src_outro": "",
		"them_watermark": False,
		"them_watermark_logo": False,
		"them_watermark_text": False,
		"src_logo": "",
		"vi_tri_logo": "topright",
		"watermark_text": "",
		"vi_tri_text": "Bottom",
		"mau_text": "#ffffff",
		"text_chay": False,
		"toc_do_chay_text": "Normal",
		# "lach_video": False,
		"cat_dau": False,
		"so_giay_cat_dau": 0,
		"cat_duoi": False,
		"so_giay_cat_duoi": 0,
		"lat_video": False,
		"change_md5": False,
		"tang_speed": False,
		"toc_do_tang_speed": 1.0,
		"ti_le_khung_hinh": "16:9",
		"chat_luong_video": "1280|720",
		"dinh_dang_video": "mp4",
		"ten_hau_to_video": "finished"
	}))


class CauHinhTuyChon_DB():
	def __init__ (self):
		CauHinhTuyChonModel.create_table()
		CauHinhTuyChonModel.get_or_create()
	
	def insert_one (self, dict_fields):
		if "ten_cau_hinh" in dict_fields.keys():
			try:
				config = CauHinhTuyChonModel.get((CauHinhTuyChonModel.ten_cau_hinh == dict_fields['ten_cau_hinh']))
				return config, False
			except CauHinhTuyChonModel.DoesNotExist:
				dataAdd = CauHinhTuyChonModel.create(**dict_fields)
				# dataAdd, created = CauHinhTuyChonModel().get_or_create(**dict_fields)
				return dataAdd, True
	
	def select_all (self):
		return CauHinhTuyChonModel.select()
	
	def remove_one (self, id_conf):
		return CauHinhTuyChonModel.delete_by_id(id_conf)
	
	def select_one_id (self, id):
		return CauHinhTuyChonModel.select().where(CauHinhTuyChonModel.id == id).get()


class ConfigAppModel(BaseModel):
	configName = CharField(unique=True)
	configValue = TextField()


class ConfigApp_DB():
	def __init__ (self):
		ConfigAppModel.create_table()
	
	def insert_one (self, dict_fields):
		_, created = ConfigAppModel().get_or_create(**dict_fields)
		return created
	
	def select_all (self):
		return ConfigAppModel.select()
	
	def select_one_name (self, name):
		return ConfigAppModel.select().where(ConfigAppModel.configName == name).get_or_none()
	
	def select_one_id (self, id):
		return ConfigAppModel.select().where(ConfigAppModel.id == id).get()
	
	def delete_by_id (self, id):
		return ConfigAppModel.delete_by_id(id)

class ConfigEditSubModel(BaseModel):
	ten_cau_hinh = CharField( default="default")
	value = TextField(default={})


class ConfigEditSub_DB():
	def __init__ (self):
		ConfigEditSubModel.create_table()
		ConfigEditSubModel.get_or_create()
	
	def insert_one (self, dict_fields):
		if "ten_cau_hinh" in dict_fields.keys():
			# try:
			# 	config = ConfigEditSubModel.get((ConfigEditSubModel.ten_cau_hinh == dict_fields['ten_cau_hinh']))
			# 	return config, False
			# except ConfigEditSubModel.DoesNotExist:
				dataAdd = ConfigEditSubModel.create(**dict_fields)
				# dataAdd, created = CauHinhTuyChonModel().get_or_create(**dict_fields)
				return dataAdd, True
	
	def select_all (self):
		return ConfigEditSubModel.select()
	
	def remove_one (self, id_conf):
		return ConfigEditSubModel.delete_by_id(id_conf)
	
	def select_one_id (self, id):
		return ConfigEditSubModel.select().where(ConfigEditSubModel.id == id).get()
