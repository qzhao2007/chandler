import osaf.framework.QAUITestAppLib as QAUITestAppLib
import os

filePath = os.path.expandvars('$CATSREPORTDIR')
if not os.path.exists(filePath):
    filePath = os.getcwd()

#initialization
fileName = "PerfStampEvent.log"
logger = QAUITestAppLib.QALogger(os.path.join(filePath, fileName),"Perf Stamp as Event")

#action
note = QAUITestAppLib.UITestItem("Note", logger)
note.logger.Start("Stamp as an event")
note.StampAsCalendarEvent(True)
note.logger.Stop()

#verification
note.Check_DetailView({"stampEvent":True})

#cleaning
logger.Close()
