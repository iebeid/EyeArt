
class AOI:
    def __init__(self, id=0,aoiLeftTopCornerX=0, aoiLeftTopCornerY=0, aoiRightTopCornerX=0, aoiRightTopCornerY=0,
    aoiLeftBottomCornerX=0, aoiLeftBottomCornerY=0, aoiRightBottomCornerX=0, aoiRightBottomCornerY=0):
        self.id = id
        self.aoiLeftTopCornerX = aoiLeftTopCornerX
        self.aoiLeftTopCornerY = aoiLeftTopCornerY
        self.aoiRightTopCornerX = aoiRightTopCornerX
        self.aoiRightTopCornerY = aoiRightTopCornerY
        self.aoiLeftBottomCornerX = aoiLeftBottomCornerX
        self.aoiLeftBottomCornerY = aoiLeftBottomCornerY
        self.aoiRightBottomCornerX = aoiRightBottomCornerX
        self.aoiRightBottomCornerY = aoiRightBottomCornerY

    def check_sample_in_aoi(self,x,y):
        topLine = self.aoiLeftTopCornerY  # y
        bottomLine = self.aoiRightBottomCornerY  # y
        rightLine = self.aoiRightTopCornerX  # x
        leftLine = self.aoiLeftBottomCornerX  # x
        check = False
        if ((y > topLine)
                and (y < bottomLine)
                and (x > leftLine)
                and (x < rightLine)):
            check = True
        return check

class Grid:
    def __init__(self,screen_height=0,screen_width=0,image_height=0,image_width=0,grid_width=0,grid_height=0):
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.image_height = image_height
        self.image_width = image_width
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.AOIs = []
        self.image_left_top_corner_x = (self.screen_width / 2) - (self.image_width / 2)
        self.image_left_top_corner_y = (self.screen_height / 2) - (self.image_height / 2)
        self.rows = self.grid_height
        self.cols = self.grid_width
        id = 1
        row_number = 0
        for r in range(self.rows):
            col_number = 0
            for c in range(self.cols):
                aoi_left_top_corner_x = self.image_left_top_corner_x + (col_number * (self.image_width/self.cols))
                aoi_left_top_corner_y = self.image_left_top_corner_y + (row_number * (self.image_height/self.rows))
                aoi_right_top_corner_x = aoi_left_top_corner_x + (self.image_width/self.cols)
                aoi_right_top_corner_y = aoi_left_top_corner_y
                aoi_left_bottom_corner_x = aoi_left_top_corner_x
                aoi_left_bottom_corner_y = aoi_left_top_corner_y + (self.image_height/self.rows)
                aoi_right_bottom_corner_x = aoi_left_top_corner_x + (self.image_width/self.cols)
                aoi_right_bottom_corner_y = aoi_left_top_corner_y + (self.image_height/self.rows)
                aoi = AOI(id,aoi_left_top_corner_x,aoi_left_top_corner_y,aoi_right_top_corner_x,
                          aoi_right_top_corner_y,aoi_left_bottom_corner_x,aoi_left_bottom_corner_y,
                          aoi_right_bottom_corner_x,aoi_right_bottom_corner_y)
                self.AOIs.append(aoi)
                id = id + 1
                col_number = col_number + 1
            row_number = row_number + 1

    def check_sample_in_grid(self,x,y):
        aoiValue = -1
        for aoi in self.AOIs:
            if aoi.check_sample_in_aoi(x,y):
                aoiValue = aoi.id
        return aoiValue

    def __str__(self):
        strg = ''
        for aoi in self.AOIs:
            strg = strg + "\n" + "Top Line: " + str(aoi.aoiLeftTopCornerY) + "\n" + \
                    "Bottom Line: " + str(aoi.aoiRightBottomCornerY) + "\n" + \
                    "Right Line: " + str(aoi.aoiRightTopCornerX) + "\n" + \
                    "Left Line: " + str(aoi.aoiLeftBottomCornerX) + "\n"
        return strg