"""
Chandler startup

@version:   $Revision$
@date:      $Date$
@copyright: Copyright (c) 2003-2005 Open Source Applications Foundation
@license:   http://osafoundation.org/Chandler_0.1_license_terms.htm
"""

import os, PyLucene
import application.Globals as Globals
import application.Utility as Utility
from i18n import OSAFMessageFactory as _


def main():

    # Process any command line switches and any environment variable values
    Globals.options = Utility.initOptions()

    def realMain():
        
        Utility.initProfileDir(Globals.options)
        
        Globals.chandlerDirectory = Utility.locateChandlerDirectory()
    
        os.chdir(Globals.chandlerDirectory)
        Utility.initLogging(Globals.options)
        Utility.initI18n(Globals.options)

        if __debug__ and Globals.options.wing:
            # Check for -wing command line argument; if specified, try to 
            # connect to an already-running WingIDE instance. See
            # http://wiki.osafoundation.org/bin/view/Chandler/DebuggingChandler#wingIDE
            # for details.

            import wingdbstub

        if __debug__ and Globals.options.komodo:
            # Check for -komodo command line argument; if specified, try to 
            # connect to an already-running Komodo instance. See
            # http://wiki.osafoundation.org/bin/view/Chandler/DebuggingChandler#Komodo
            # for details.

            import dbgp.client
            dbgp.client.brk()

        from application.Application import wxApplication

        # Redirect stdio and stderr to a dialog if we're running the debug 
        # version. This is done to catch asserts, which otherwise will never
        # get seen by people who run Chandler using the launchers, e.g.
        # Aparna. If you're running release you can also set things up so 
        # that you can see stderr and stdout if you run in a shell or from
        # wing with a console.
        #
        # useBestVisual - uses best screen resolutions on some old computers.
        #                 See wxApp.SetUseBestVisual

        redirect = __debug__ and not Globals.options.stderr
        app = wxApplication(redirect=redirect, useBestVisual=True)

        app.MainLoop()

    if Globals.options.nocatch:
        # When debugging, it's handy to run without the outer exception frame
        realMain()
    else:
        # The normal way: wrap the app in an exception frame
        from repository.persistence.RepositoryError \
            import RepositoryOpenDeniedError, ExclusiveOpenDeniedError

        try:
            import logging, wx
            realMain()

        except (RepositoryOpenDeniedError, ExclusiveOpenDeniedError):
            # XXX [i18n] Dunno how this could be translated
            message = "Another instance of Chandler currently has the " \
                      "repository open."
            logging.error(message)
            dialog = wx.MessageDialog(None, message, "Chandler", 
                                      wx.OK | wx.ICON_INFORMATION)
            dialog.ShowModal()
            dialog.Destroy()

        except Utility.SchemaMismatchError:
            logging.info("User chose not to clear the repository.  Exiting.")

        except Exception, e:
            import sys, traceback
            type, value, stack = sys.exc_info()
            backtrace = traceback.format_exception(type, value, stack)

            line1 = _(u"Chandler encountered an unexpected problem while trying to start.\n")

            longMessage = "".join([line1, "\n"] + backtrace)

            logging.error (longMessage)

            if os.linesep != '\n':
                longMessage = longMessage.replace ('\n', os.linesep)

            wx.TheClipboard.SetData (wx.TextDataObject (longMessage))

            frames = 8
            line2 = _(u"Here are the bottom %(frames)s frames of the stack:\n") % {'frames': frames - 1}
            line3 = _(u"The clipboard contains the stack trace.\n")
            shortMessage = "".join ([line1, line2, "\n"] + backtrace[-frames:] + ["\n", line3])

            if wx.GetApp() is None:
                app = wx.PySimpleApp()

            dialog = wx.MessageDialog(None, shortMessage, "Chandler", 
                                      wx.OK | wx.ICON_INFORMATION)
            dialog.ShowModal()
            dialog.Destroy()


    #@@@Temporary testing tool written by Morgen -- DJA
    #import util.timing
    #print "\nTiming results:\n"
    #util.timing.results()

if __name__== "__main__":
    main()