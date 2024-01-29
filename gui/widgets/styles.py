def tab_main_style():
    return f"""
        QTabWidget#tabWidget::pane {{ /* The tab content */
            border: 0px solid #C2C7CB;
            margin-top:5px;
        }} 
        QTabWidget#tabWidget::tab-bar {{ /* nguyên khối các tab */
            alignment: left;
        }}
         QTabWidget#tabWidget QTabBar::tab {{ /* từng tab */
            background-color: rgba(255, 255, 255, 0);
            color:#ffffff;
            margin-left:5px;
            min-width: 20px;
            padding: 8px 5px ;
            font-family:"Segoe UI";
        }}  
       QTabWidget#tabWidget QTabBar::tab:selected,QTabWidget#tabWidget QTabBar::tab:hover {{ /*  tab active và tab hover*/
           background-color: rgb(0, 170, 255);
        }}
         QTabWidget#tabWidget QTabBar::tab:selected {{ /*  tab active */
            color:#ffffff;
            font: bold;
            border-bottom: 3px solid #fcff00;
        }}
       QTabWidget#tabWidget  QTabBar::tab:!selected{{ /*  tab ko đc active */
            margin-top: 0px;
        }}
         QTabWidget#tabWidget QTabBar::tab::first:selected {{ /*  tab đầu tiên đc active */
            
        }}
       QTabWidget#tabWidget  QTabBar::tab:only-one  {{ /*  chỉ có 1 tab */
               margin: 0;
        }}
    
        """
