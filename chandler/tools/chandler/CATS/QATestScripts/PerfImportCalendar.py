import osaf.sharing.Sharing as Sharing
import osaf.sharing.ICalendar as ICalendar
import osaf.framework.QAUITestAppLib as QAUITestAppLib
import os, wx
import osaf.pim as pim

App_ns = QAUITestAppLib.App_ns

filePath = os.path.expandvars('$CATSREPORTDIR')
if not os.path.exists(filePath):
    filePath = os.getcwd()

# initialization
fileName = "PerfImporting.log"
logger = QAUITestAppLib.QALogger(os.path.join(filePath, fileName),"Importing 3000 event calendar")


path = os.path.join(os.path.expandvars('$CATSHOME'),"QATestScripts")
print path
share = Sharing.OneTimeFileSystemShare(path, 'Generated3000.ics', ICalendar.ICalendarFormat, view=App_ns.itsView)

logger.Start("Import Large Calendar")
try:
	collection = share.get()
except:
	logger.Stop()
	logger.ReportFailure("Importing calendar: exception raised")
else:
	App_ns.root.AddToSidebarWithoutCopying({'items' : [collection]})	
	wx.GetApp().Yield()
	logger.Stop()
	logger.ReportPass("Importing calendar")

def TestEventCreation(title):
    global logger
    global App_ns
    global pim
    testEvent = App_ns.item_named(pim.CalendarEvent, title)
    if testEvent is not None:
        logger.ReportPass("Testing event creation: '%s'" % title)
    else:
        logger.ReportFailure("Testing event creation: '%s' not created" % title)

TestEventCreation("Go to the beach")
TestEventCreation("Basketball game")
TestEventCreation("Visit friend")
TestEventCreation("Library")


logger.SetChecked(True)
logger.Report("Import")
logger.Close()

