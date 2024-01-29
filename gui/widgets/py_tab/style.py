# STYLE
# ///////////////////////////////////////////////////////////////
style = '''
/* /////////////////////////////////////////////////////////////////////////////////////////////////
QTableWidget */

QTableWidget {{	
	
	padding: 5px;
	border-radius: {_radius}px;
	gridline-color: {_grid_line_color};
    color: {_color};
   
}}
QTableView {{
background-color: {_bg_color};
}}

QTableWidget::item{{
 
	gridline-color: rgb(44, 49, 60);
}}

QTableWidget::item:selected{{
    padding:0;
 	background-color: rgba(172,219,255,0.2);
 	color: #00ff48;
}}
QTableWidget::item:selected:focus{{
  
}}
 
QHeaderView::section{{
	background-color: rgb(33, 37, 43);
	max-width: 30px;
	border: 1px solid rgb(44, 49, 58);
	border-style: none;
    border-bottom: 1px solid rgb(44, 49, 60);
    border-right: 1px solid rgb(44, 49, 60);
}}
QTableWidget::horizontalHeader {{	
	background-color: rgb(33, 37, 43);
}}
QTableWidget QTableCornerButton::section {{
    border: none;
	background-color: {_header_horizontal_color};
	padding: 3px;
    border-top-left-radius: {_radius}px;
}}
QHeaderView::section:horizontal
{{
    border: none;
	background-color: {_header_horizontal_color};
	padding-left: 3px;
}}
QHeaderView::section:vertical
{{
    border: none;
	background-color: {_header_vertical_color};
	padding-left: 5px;
    padding-right: 5px;
    border-bottom: 1px solid {_bottom_line_color};
    margin-bottom: 1px;
}}


/* /////////////////////////////////////////////////////////////////////////////////////////////////
ScrollBars */
QScrollBar:horizontal {{
    border: none;
    background: {_scroll_bar_bg_color};
    height: 8px;
    margin: 0px 21px 0 21px;
	border-radius: 0px;
}}
QScrollBar::handle:horizontal {{
    background: {_context_color};
    min-width: 25px;
	border-radius: 4px
}}
QScrollBar::add-line:horizontal {{
    border: none;
    background: {_scroll_bar_btn_color};
    width: 20px;
	border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}}
QScrollBar::sub-line:horizontal {{
    border: none;
    background: {_scroll_bar_btn_color};
    width: 20px;
	border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    subcontrol-position: left;
    subcontrol-origin: margin;
}}
QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal
{{
     background: none;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
{{
     background: none;
}}
QScrollBar:vertical {{
	border: none;
    background: {_scroll_bar_bg_color};
    width: 8px;
    margin: 21px 0 21px 0;
	border-radius: 0px;
}}
QScrollBar::handle:vertical {{	
	background: {_context_color};
    min-height: 25px;
	border-radius: 4px
}}
QScrollBar::add-line:vertical {{
     border: none;
    background: {_scroll_bar_btn_color};
     height: 20px;
	border-bottom-left-radius: 4px;
    border-bottom-right-radius: 4px;
     subcontrol-position: bottom;
     subcontrol-origin: margin;
}}
QScrollBar::sub-line:vertical {{
	border: none;
    background: {_scroll_bar_btn_color};
     height: 20px;
	border-top-left-radius: 4px;
    border-top-right-radius: 4px;
     subcontrol-position: top;
     subcontrol-origin: margin;
}}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
     background: none;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
     background: none;
}}


'''
style_button = '''

QPushButton {{
    padding:5px 10px;
    border-radius: {_radius};	
 
    }}
QPushButton#btn_stop {{
    background-color: {_bg_color_button_action_stop};
    }}
QPushButton#btn_pause {{
    background-color: {_bg_color_button_action_pause};
}}
    
QPushButton#btn_stop:hover {{
    background-color: {_bg_color_hover_stop};
    }}
    
QPushButton#btn_stop:pressed {{	
    background-color: {_bg_color_pressed_stop};
    }}
    
QPushButton#btn_stop:disabled, QPushButton#btn_pause:disabled  {{	
background-color: {_bg_color_disable_button_action};
color:{_color_disable_button_action};

}}
 

QPushButton#btn_pause:hover {{
    background-color: {_bg_color_hover_pause};
    }}
    
QPushButton#btn_pause:pressed {{	
    background-color: {_bg_color_pressed_pause};
    }}
                
'''