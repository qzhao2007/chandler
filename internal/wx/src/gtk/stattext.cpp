/////////////////////////////////////////////////////////////////////////////
// Name:        stattext.cpp
// Purpose:
// Author:      Robert Roebling
// Id:          $Id: stattext.cpp,v 1.63 2006/02/04 00:09:16 MR Exp $
// Copyright:   (c) 1998 Robert Roebling
// Licence:     wxWindows licence
/////////////////////////////////////////////////////////////////////////////

// For compilers that support precompilation, includes "wx.h".
#include "wx/wxprec.h"

#if wxUSE_STATTEXT

#include "wx/stattext.h"
#include "wx/gtk/private.h"

#include "gdk/gdk.h"
#include "gtk/gtk.h"

extern "C"
void wxgtk_window_size_request_callback(GtkWidget *widget,
                                        GtkRequisition *requisition,
                                        wxWindow *win);

//-----------------------------------------------------------------------------
// wxStaticText
//-----------------------------------------------------------------------------

IMPLEMENT_DYNAMIC_CLASS(wxStaticText,wxControl)

wxStaticText::wxStaticText()
{
}

wxStaticText::wxStaticText(wxWindow *parent,
                           wxWindowID id,
                           const wxString &label,
                           const wxPoint &pos,
                           const wxSize &size,
                           long style,
                           const wxString &name)
{
  Create( parent, id, label, pos, size, style, name );
}

bool wxStaticText::Create(wxWindow *parent,
                          wxWindowID id,
                          const wxString &label,
                          const wxPoint &pos,
                          const wxSize &size,
                          long style,
                          const wxString &name )
{
    m_needParent = TRUE;

    if (!PreCreation( parent, pos, size ) ||
        !CreateBase( parent, id, pos, size, style, wxDefaultValidator, name ))
    {
        wxFAIL_MSG( wxT("wxStaticText creation failed") );
        return FALSE;
    }

    // notice that we call the base class version which will
    // not set the label's text to it because the label is no
    // yet created and because SetLabel() has a side
    // effect of changing the control size which might not be desirable
    // wxContro::SetLabel no longer strips menu codes, so do it here.
    wxString label1(wxStripMenuCodes(label));
    wxControl::SetLabel(label);
    m_widget = gtk_label_new( wxGTK_CONV( label1 ) );

    GtkJustification justify;
    if ( style & wxALIGN_CENTER )
      justify = GTK_JUSTIFY_CENTER;
    else if ( style & wxALIGN_RIGHT )
      justify = GTK_JUSTIFY_RIGHT;
    else // wxALIGN_LEFT is 0
      justify = GTK_JUSTIFY_LEFT;
    gtk_label_set_justify(GTK_LABEL(m_widget), justify);

    // GTK_JUSTIFY_LEFT is 0, RIGHT 1 and CENTER 2
    static const float labelAlignments[] = { 0.0, 1.0, 0.5 };
    gtk_misc_set_alignment(GTK_MISC(m_widget), labelAlignments[justify], 0.0);

        gtk_label_set_line_wrap( GTK_LABEL(m_widget), TRUE );

    m_parent->DoAddChild( this );

    PostCreation(size);

    // the bug below only happens with GTK 2
    if ( justify != GTK_JUSTIFY_LEFT )
    {
        // if we let GTK call wxgtk_window_size_request_callback the label
        // always shrinks to its minimal size for some reason and so no
        // alignment except the default left doesn't work (in fact it does,
        // but you don't see it)
        g_signal_handlers_disconnect_by_func (m_widget,
                                              (gpointer) wxgtk_window_size_request_callback,
                                              this);
    }

    return TRUE;
}

wxString wxStaticText::GetLabel() const
{
    GtkLabel *label = GTK_LABEL(m_widget);
    wxString str = wxGTK_CONV_BACK( gtk_label_get_text( label ) );

    return wxString(str);
}

void wxStaticText::SetLabel( const wxString &label )
{
    wxControl::SetLabel(label);
    wxString label1(wxStripMenuCodes(label));

    // Build the colorized version of the label (markup only allowed
    // under GTK2):
    // FIXME: Does this handle background correct? I recall bug reports - MR
    if (m_foregroundColour.Ok())
    {
        // If the color has been set, create a markup string to pass to
        // the label setter
        wxString colorlabel;
        colorlabel.Printf(_T("<span foreground=\"#%02x%02x%02x\">%s</span>"),
                          m_foregroundColour.Red(), m_foregroundColour.Green(),
                          m_foregroundColour.Blue(),
                          wxEscapeStringForPangoMarkup(label1).c_str());
        gtk_label_set_markup( GTK_LABEL(m_widget), wxGTK_CONV( colorlabel ) );
    }
    else
        gtk_label_set_text( GTK_LABEL(m_widget), wxGTK_CONV( label1 ) );

    // adjust the label size to the new label unless disabled
    if (!HasFlag(wxST_NO_AUTORESIZE))
    {
        InvalidateBestSize();
        SetSize( GetBestSize() );
    }
}

bool wxStaticText::SetFont( const wxFont &font )
{
    bool ret = wxControl::SetFont(font);

    // adjust the label size to the new label unless disabled
    if (!HasFlag(wxST_NO_AUTORESIZE))
    {
        InvalidateBestSize();
        SetSize( GetBestSize() );
    }
    return ret;
}

void wxStaticText::DoSetSize(int x, int y,
                           int width, int height,
                           int sizeFlags )
{
    wxControl::DoSetSize( x, y, width, height, sizeFlags );
}

wxSize wxStaticText::DoGetBestSize() const
{
    // Do not return any arbitrary default value...
    wxASSERT_MSG( m_widget, wxT("wxStaticText::DoGetBestSize called before creation") );

    // GetBestSize is supposed to return unwrapped size
    gtk_label_set_line_wrap( GTK_LABEL(m_widget), FALSE );

    GtkRequisition req;
    req.width = -1;
    req.height = -1;
    (* GTK_WIDGET_CLASS( GTK_OBJECT_GET_CLASS(m_widget) )->size_request )
        (m_widget, &req );

    gtk_label_set_line_wrap( GTK_LABEL(m_widget), TRUE );

    return wxSize (req.width, req.height);
}

bool wxStaticText::SetForegroundColour(const wxColour& colour)
{
    // First, we call the base class member
    wxControl::SetForegroundColour(colour);
    // Then, to force the color change, we set the label with the current label
    SetLabel(GetLabel());
    return true;
}

// static
wxVisualAttributes
wxStaticText::GetClassDefaultAttributes(wxWindowVariant WXUNUSED(variant))
{
    return GetDefaultAttributesFromGTKWidget(gtk_label_new);
}

#endif // wxUSE_STATTEXT
