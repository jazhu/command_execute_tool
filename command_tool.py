# -*- coding: utf-8 -*- 

#创建人：393620170@qq.com
#输出时间：2018年6月20日21:45
#版本：v1.0.3-定制 
#基于python3.6的环境开发

import paramiko
import time
import os
import sys
import wx
import wx.xrc
import threading


###########################################################################
#导入命令模板函数
def run():
    global gcmd
    if len(gcmd)>0:   
        cmd_list=gcmd.split('\n')
    else:
        cmd_list=['show version','show interface']
    frame.statusbar.SetStatusText('开始执行命令.....',0)  
    t=threading.Thread(target=login, args=(frame.ip.GetValue(),int(frame.port.GetValue()),frame.user.GetValue(),frame.password.GetValue(),cmd_list))
    t.start()
	
#执行show命令
def exec_cmd(channel,cmdlist):
    frame.mgauge.SetRange(len(cmdlist))#进度条
    guagevalue=1
    fulllog=open('my.log','wb')#创建日志文件
    for cmd in cmdlist:
        frame.mgauge.SetValue(guagevalue)#更新进度条
        #frame.out.AppendText('\n执行命令： '+cmd+'\n')
        frame.statusbar.SetStatusText('命令执行中，正在执行第'+str(guagevalue)+'个命令！',0)  #输出状态栏
        channel.send(cmd+' \n') #执行命令
        time.sleep(1) #歇会        
        temp= channel.recv(32768)  #接收输出
        while  not temp.endswith(b'# '):#判断是否接收完毕，注意结尾有空格
            temp+=channel.recv(32768)
        frame.out.AppendText(temp.decode())#界面输出接收到的内容
        outlog = temp.decode('utf-8', 'replace') #程序输出的内容的byte转换str，
        fulllog.write(outlog.encode('utf-8', 'replace')) #写入日志文件  
        #log.close #关闭写入，养成好习惯
        guagevalue+=1
    fulllog.close()#保存日志文件



def login(host,port,username,password,cmd_list):
    #连接设备
    
    frame.out.Clear()#清除窗口内容
    frame.out.AppendText('正在连接设备中...\n')
    frame.statusbar.SetStatusText('设备连接中......',0)
    try:
        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=port, username=username, password=password,timeout=30)#连接设备
    except:
        frame.out.AppendText('设备登录失败，请检查输入参数！\n')
        wx.MessageBox('设备登录失败，请检查输入参数！', "错误" ,wx.OK | wx.ICON_INFORMATION) 
        frame.collet.Enable()
    #创建对象，后面就靠这个对象了
    chan = ssh.invoke_shell()
    while not chan.recv_ready():
        time.sleep(1)
    chan.send('terminal length 0\n') #用于山石设备设置终端输出显示命令   
    chan.send('terminal width 512\n')#用于山石设备设置终端输出显示命令   
    time.sleep(1)
    #循环执行cmd.txt的命令
    temp=''
    out=''
    frame.out.AppendText('设备登录成功！\n')

    time.sleep(1)
    wx.MessageBox('确认要开始执行命令吗？', "提示" ,wx.OK | wx.ICON_INFORMATION)
    exec_cmd(chan,cmd_list)#执行命令  
    frame.collet.Enable()
    frame.statusbar.SetStatusText('执行完毕！',0)   
    ssh.close() #关闭SSH连接


#读取命令模板文件并输出到程序窗口
def get_file():
    global gcmd
    wildcard = "Text Files (*.txt)|*.txt"
    dlg = wx.FileDialog(frame, "选择命令模板文件", os.getcwd(), "", wildcard, wx.FD_OPEN)
    if dlg.ShowModal() == wx.ID_OK: 
        f = open(dlg.GetPath(), 'r',encoding='UTF-8')
        with f:
            gcmd= f.read()          
            frame.out.SetValue(gcmd)
    frame.statusbar.SetStatusText('命令文件路径：'+dlg.GetPath(),0)
    dlg.Destroy()



#弹出对话框
class MyDialog(wx.Dialog): 
   def __init__(self, parent, title): 
      super(MyDialog, self).__init__(parent, title = title, size = (250,150)) 
      panel = wx.Panel(self) 
      self.btn = wx.Button(panel, wx.ID_OK, label = "ok", size = (50,20), pos = (75,50))



class Mywin ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"命令执行工具v0.1", pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_FRAME_STYLE )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetFont( wx.Font( 14, 70, 90, 90, False, "微软雅黑" ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVEBORDER ) )
		
		gbSizer5 = wx.GridBagSizer( 10, 0 )
		gbSizer5.SetFlexibleDirection( wx.BOTH )
		gbSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_ip = wx.StaticText( self, wx.ID_ANY, u"设备地址：", wx.DefaultPosition, wx.Size( 100,-1 ), wx.ALIGN_RIGHT )
		self.m_ip.Wrap( -1 )
		self.m_ip.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		
		gbSizer5.Add( self.m_ip, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.ip = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.ip.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		
		gbSizer5.Add( self.ip, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_port = wx.StaticText( self, wx.ID_ANY, u"SSH端口：", wx.DefaultPosition, wx.Size( 100,-1 ), wx.ALIGN_RIGHT )
		self.m_port.Wrap( -1 )
		self.m_port.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		
		gbSizer5.Add( self.m_port, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.port = wx.TextCtrl( self, wx.ID_ANY, u"22", wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.port.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		
		gbSizer5.Add( self.port, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_user = wx.StaticText( self, wx.ID_ANY, u"用户名：", wx.DefaultPosition, wx.Size( 100,-1 ), wx.ALIGN_RIGHT )
		self.m_user.Wrap( -1 )
		self.m_user.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		
		gbSizer5.Add( self.m_user, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.user = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.user.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		
		gbSizer5.Add( self.user, wx.GBPosition( 3, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_password = wx.StaticText( self, wx.ID_ANY, u"密码：", wx.DefaultPosition, wx.Size( 100,-1 ), wx.ALIGN_RIGHT )
		self.m_password.Wrap( -1 )
		self.m_password.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		
		gbSizer5.Add( self.m_password, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.password = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), wx.TE_PASSWORD )
		self.password.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		
		gbSizer5.Add( self.password, wx.GBPosition( 4, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.collet = wx.Button( self, wx.ID_ANY, u"开始", wx.DefaultPosition, wx.Size( 160,-1 ), wx.BU_EXACTFIT|wx.NO_BORDER )
		self.collet.SetFont( wx.Font( 11, 74, 90, 90, False, "微软雅黑" ) )
		self.collet.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
		self.collet.SetBackgroundColour( wx.Colour( 0, 64, 128 ) )
		
		gbSizer5.Add( self.collet, wx.GBPosition( 3, 4 ), wx.GBSpan( 2, 1 ), wx.ALL, 5 )
		
		self.importcmd = wx.Button( self, wx.ID_ANY, u"导入命令", wx.DefaultPosition, wx.Size( 160,-1 ), wx.BU_EXACTFIT|wx.NO_BORDER )
		self.importcmd.SetFont( wx.Font( 11, 74, 90, 90, False, "微软雅黑" ) )
		self.importcmd.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
		self.importcmd.SetBackgroundColour( wx.Colour( 0, 64, 128 ) )
		
		gbSizer5.Add( self.importcmd, wx.GBPosition( 1, 4 ), wx.GBSpan( 2, 1 ), wx.ALL, 5 )
		
		self.report = wx.Button( self, wx.ID_ANY, u"生成巡检报告", wx.DefaultPosition, wx.Size( 160,-1 ), wx.NO_BORDER )
		self.report.SetFont( wx.Font( 11, 74, 90, 90, False, "微软雅黑" ) )
		self.report.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
		self.report.SetBackgroundColour( wx.Colour( 0, 64, 128 ) )
		self.report.Hide()
		
		gbSizer5.Add( self.report, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.out = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.Size( 760,270 ), wx.TE_MULTILINE )
		self.out.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		
		gbSizer5.Add( self.out, wx.GBPosition( 6, 1 ), wx.GBSpan( 1, 6 ), wx.ALL, 5 )
		
		self.mgauge = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size( 630,-1 ), wx.GA_HORIZONTAL )
		self.mgauge.SetValue( 0 ) 
		gbSizer5.Add( self.mgauge, wx.GBPosition( 5, 2 ), wx.GBSpan( 1, 6 ), wx.ALL, 5 )

		self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"进度：", wx.DefaultPosition, wx.Size( 100,-1 ), wx.ALIGN_RIGHT)
		self.m_staticText5.Wrap( -1 )
		self.m_staticText5.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		gbSizer5.Add( self.m_staticText5, wx.GBPosition( 5, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.SetSizer( gbSizer5 )
		self.Layout()
		self.statusbar = self.CreateStatusBar( 1, 0, wx.ID_ANY )
		self.statusbar.SetFont( wx.Font( 9, 74, 90, 90, False, "微软雅黑" ) )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.collet.Bind( wx.EVT_BUTTON, self.g )
		self.importcmd.Bind( wx.EVT_BUTTON, self.l )
		self.report.Bind( wx.EVT_BUTTON, self.output )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def l( self, event ):
		get_file()
	
	def g( self, event ):
		run()
		self.collet.Enable( False )
	
	def output( self, event ):
		event.Skip()
	




#程序开始


app = wx.App()
frame = Mywin(None)
frame.Show(True)
global gcmd
gcmd=[]
app.MainLoop() 
        
