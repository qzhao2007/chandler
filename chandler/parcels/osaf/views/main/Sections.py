import wx

from osaf.framework.blocks import ControlBlocks
from util.divisions import get_divisions

from osaf.framework.blocks import DrawingUtilities

from i18n import OSAFMessageFactory as _

class SectionedGridDelegate(ControlBlocks.AttributeDelegate):

    def InitElementDelegate(self):
        # indexes of item in blockItem.contents that designate the
        # start of a new section
        self.sectionIndexes = []

        # an array of (row, length) where row is the row that has a
        # section header, and length is the number of rows following
        # that section header. Note that length+1 is the number of
        # rows including the section header
        self.sectionRows = []

        # a set indicating which sections are collapsed
        self.collapsedSections = set()

        # total rows in the table
        self.totalRows = 0

        self.RegisterDataType("Section", SectionRenderer(), None)
        
    def SynchronizeDelegate(self):
        """
        its reasonably cheap to rebuild section indexes, as
        get_divisions is really optimized for this
        """

        self.RebuildSections()

    def RebuildSections(self):
        """
        rebuild the sections - this is relatively cheap as long as
        there aren't a lot of sections
        """
        indexName = self.blockItem.contents.indexName
        self.sectionRows = []
        self.totalRows = 0
        
        # regenerate index-based sections - each entry in
        # self.sectionIndexes is the first index in the collection
        # where we would need a section
        if indexName in (None, '__adhoc__'):
            self.sectionIndexes = []
        else:
            self.sectionIndexes = \
                get_divisions(self.blockItem.contents,
                              key=lambda x: getattr(x, indexName))

        # dont' show section headers for zero or one section
        if len(self.sectionIndexes) <= 1:
            self.totalRows = len(self.blockItem.contents)
            return
            
        # now build the row-based sections - each entry in this array
        # is the actual row that contains the section divider
        nextSectionRow = 0
        for section in range(0, len(self.sectionIndexes)):
            sectionRow = nextSectionRow
            if section in self.collapsedSections:
                sectionLength = 0
                # previous section collapsed, so we're just one past
                # the last one
            else:
                if section == len(self.sectionIndexes)-1:
                    # last section - need to use blockItem.contents
                    # to determine the length
                    sectionLength = (len(self.blockItem.contents) -
                                     self.sectionIndexes[-1])
                else:
                    # not collapsed, so determine the length of this
                    # section from the next section in self.sectionIndexes
                    sectionLength = (self.sectionIndexes[section+1] -
                                     self.sectionIndexes[section])

            # might as well recall this for the next iteration through
            # the loop. the +1 is for the section header itself.
            nextSectionRow = sectionRow + sectionLength + 1
            
            self.sectionRows.append((sectionRow, sectionLength))
            self.totalRows += sectionLength + 1

        # make sure we're sane
        assert len(self.sectionRows) == len(self.sectionIndexes)
        assert sum([length+1 for (row, length) in self.sectionRows]) == \
               self.totalRows
                   

    def GetElementCount(self):
        return self.totalRows

    def GetElementType(self, row, column):
        itemIndex = self.RowToIndex(row)
        if itemIndex == -1:
            return "Section"

        return super(SectionedGridDelegate, self).GetElementType(row, column)

    def ReadOnly(self, row, column):
        itemIndex = self.RowToIndex(row)
        if itemIndex == -1:
            return True, True

        return super(SectionedGridDelegate, self).ReadOnly(row, column)
    
    def GetElementValue(self, row, column):
        
        itemIndex = self.RowToIndex(row)
        if itemIndex == -1:
            # section headers: we get the section title from the next row
            firstItemIndex = self.RowToIndex(row+1)
            firstItemInSection = self.blockItem.contents[firstItemIndex]
            
            indexAttribute = self.blockItem.contents.indexName
            return (firstItemInSection, indexAttribute)
        
        attributeName = self.blockItem.columnData[column]
        return (self.blockItem.contents [itemIndex], attributeName)

    def RowToIndex(self, row):
        """
        Map Row->Index taking into account collapsed sections.

        Right now this is a linear search of sections - if we need to
        worry about performance then we probably need to switch to a
        binary search. Generally, there aren't many sections so we
        won't optimize this.
        """

        if len(self.sectionRows) == 0:
            return row

        sectionAdjust = len(self.sectionRows) - 1
        # search backwards so we can jump right to the section number
        for (reversedSection, (sectionRow, sectionSize)) in enumerate(reversed(self.sectionRows)):
            section = sectionAdjust - reversedSection
            
            if row == sectionRow:
                # this row is a section header, there is no valid data
                # row here
                return -1
            
            if row > sectionRow:
                # We are in an expanded section. We need to find the
                # relative position of this row within the section,
                # and then go look up that relative position in
                # self.sectionIndexes (+1 accounts for the header row)
                
                rowOffset = row - (sectionRow + 1)
                itemIndex = self.sectionIndexes[section] + rowOffset
                
                assert itemIndex < len(self.blockItem.contents)
                return itemIndex

        assert False, "Couldn't find index for row %s in %s" % (row, [x[0] for x in reversed(self.sectionRows)])

    def IndexToRow(self, itemIndex):
        """
        Find the row for the corresponding item. This is done with a
        linear search through the sections. Generally there aren't a
        lot of sections though so this should be reasonably fast.
        """
        if len(self.sectionIndexes) == 0:
            return itemIndex

        sectionAdjust = len(self.sectionIndexes) - 1
        for reversedSection, sectionIndex in enumerate(reversed(self.sectionIndexes)):
            section = sectionAdjust - reversedSection
            
            if itemIndex > sectionIndex:
                if section in self.collapsedSections:
                    # section is collapsed! That's not good. Perhaps
                    # we should assert? Or maybe this is a valid case?
                    return -1
                else:
                    # Expanded sxection. Find the relative position
                    # +1 accounts for header row
                    indexOffset = itemIndex - sectionIndex
                    sectionRow = self.sectionRows[section][0]
                    row = (sectionRow + 1) + indexOffset
                    assert row < self.totalRows
                    
                    return row

        assert False, "Couldn't find row for index %s" % itemIndex


    def CollapseSection(self, section):
        """
        Collapse a given section - i.e. make it zero-length
        """
        assert section not in self.collapsedSections

        # subtract the oldLength
        (oldPosition, oldLength) = self.sectionRows[section]

        self.AdjustSectionPosition(section, -oldLength)
            
    def ExpandSection(self, section):
        """
        Expand the given section to be the same as the original data
        """
        assert section not in self.collapsedSections

        # we look back in the original data to find the section length
        if section == len(self.sectionIndexes) - 1:
            # last section, need to look this up
            newLength = (len(self.blockItem.contents) - 
                         self.sectionIndexes[section])
        else:
            newLength = (self.sectionIndexes[section+1] -
                         self.sectionIndexes[section])

        self.AdjustSectionPosition(section, newLength)

    def AdjustSectionPosition(self, startSection, delta):
        """
        Adjust a section's position by delta - may be positive or
        negative. Since section positions are somewhat interdependent,
        we have to adjust the given section as well as all sections
        following it.
        """
        for sectionNum, (sectionPosition, sectionLength) \
                in range(section, len(self.sectionRows)):
            
            self.sectionRows[sectionNum] = (sectionPosition + delta,
                                            sectionLength)
        

class SectionRenderer(wx.grid.PyGridCellRenderer):
    def __init__(self, *args, **kwds):
        super(SectionRenderer, self).__init__(*args, **kwds)
        self.brushes = DrawingUtilities.Gradients()
        
    def ReadOnly(self, *args):
        return True

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        (firstItem, attributeName) = grid.GetElementValue(row, col)
        
        dc.SetPen(wx.TRANSPARENT_PEN)
        brush = self.brushes.GetGradientBrush(0, rect.height,
                                              (153, 204, 255), (203, 229, 255),
                                              "Vertical")
        dc.SetBrush(brush)
        dc.DrawRectangleRect(rect)

        if col == 0:
            dc.SetTextForeground(wx.BLACK)
            dc.SetBackgroundMode(wx.TRANSPARENT)
            sectionTitle = _(u"Section: %s") % getattr(firstItem, attributeName, "[None]")
            dc.DrawText(sectionTitle, 3, rect.y + 2)


