from Tkinter import *
import random
import direct
import processImg

class WNFA_GUI(Frame):
    
    def __init__(self,master=None, coord=[]):
        Frame.__init__(self,master);
        
        self.start_x = -10
        self.start_y = -10
        self.mag = 60   
        self.rows = 9   
        self.cols = 11 
        self.orginal_x = 380
        self.orginal_y = 320  

        canvas_width = 760
        canvas_height = 670
        self.w = Canvas(master, width=canvas_width, height=canvas_height)
        self.w.pack()
        self.drawGrid()
        self.addLabel()
        self.redraw(1000,coord)

    def addLabel(self):
                          
        x_Start = -330
        y_Start = 270
                          
        for i in range(0,self.cols+1):    
            # widget_top = Label(self.w, text=x_Start, fg='black')
            # widget_buttom = Label(self.w, text=x_Start, fg='black')
            # x_Start = x_Start + self.mag
    
            # self.w.create_window(50+i*self.mag, 35, window=widget_top) 
            # self.w.create_window(50+i*self.mag, 605, window=widget_buttom)
            self.w.create_text(50+i*self.mag, 35, text=y_Start)
            self.w.create_text(50+i*self.mag, 605, text=y_Start)
            x_Start = x_Start + self.mag

        for i in range(0,self.rows+1):           
            # widget_right = Label(self.w, text=y_Start, fg='black')
            # widget_left = Label(self.w, text=y_Start, fg='black')
            # y_Start = y_Start - self.mag
    
            # self.w.create_window(30, 50+i*self.mag, window=widget_right) 
            # self.w.create_window(730, 50+i*self.mag, window=widget_left)
            self.w.create_text(30, 50+i*self.mag, text=y_Start)
            self.w.create_text(730, 50+i*self.mag, text=y_Start)
            y_Start = y_Start - self.mag

    def drawGrid(self):
       
        actual_coord = [(240,-180),(300,-30),(240,90),(150,120),(30,120),(-90,120),(-210,90)\
                    ,(-270,30),(-270,-90),(-210,-180),(-90,-210),(30,-210),(150,-210)]

        for i in range(0,self.cols+1):
            self.w.create_line(self.start_x + (i+1)*self.mag, self.start_y + self.mag,\
                               self.start_x + (i+1)*self.mag, self.start_y + (self.rows+1)*self.mag, fill='#6495ed')
        for i in range(0,self.rows+1):
            self.w.create_line(self.start_x + self.mag, self.start_y + (i+1)*self.mag,\
                               self.start_x + self.mag*(1+self.cols), self.start_y + (i+1)*self.mag, fill='#6495ed')
        self.w.create_line(380, 30, 380, 620, fill="#1f1f1f", dash=(4, 4))
        self.w.create_line(10 , 320, 750, 320, fill="#1f1f1f", dash=(4, 4))
        

        trans1 = self.w.create_oval(375,315,385,325,fill = '#8b4513')
        trans2 = self.w.create_oval(354,336,364,346,fill = '#8b4513')
        trans3 = self.w.create_oval(396,336,406,346,fill = '#8b4513')

        #print actual rx position text
        for i in actual_coord:

            label = "(" + str(i[0]) + "," + str(i[1]) + ")" 
            x = self.orginal_x + i[0]
            y = self.orginal_y - i[1]
            actual_point = self.w.create_oval(x-5,y-5,x+5,y+5,fill='orange')
            actual_coord_label = self.w.create_text(x+30, y-15,text=label)
            # self.w.create_window(x+5, y+5, window=actual_coord_label) F

        #buttom display
        self.w.create_oval(360,645,370,655,fill = 'orange')
        self.w.create_text(428, 650, text = "Actual Rx position")
        self.w.create_oval(510,645,520,655,fill = '#8b4513')
        self.w.create_text(558, 650, text = "Transmitter")
        self.w.create_oval(620,645,630,655,fill = '#008080')
        self.w.create_text(690, 650, text = "Estimated position")

    def redraw(self, delay ,coord):
        
        if(len(coord) > 0) :
            # row = random.randint(50,580)
            # col = random.randint(50,700)
            x = self.orginal_x + coord[0][0]
            y = self.orginal_y - coord[0][1]
            print "(x,y) = (%f,%f)" %(x,y)
        
            trans1 = self.w.create_oval(x,y,x+10,y+10,fill = '#008080')
            # widget_top = Label(self.w, text=x_Start, fg='black')

            self.after(delay, lambda: self.redraw(delay, coord))
            del coord[0]

if __name__ == '__main__':
    
    path = "/Volumes/Transcend/GitHub/WNFA_FinalProject/new_src/AoA/demo"
    img_list = direct.getFileInDirectory(path);
    
    coord = []

    for img_path in img_list :
        print "img_path:",img_path
        rx_location = processImg.processRxLocation(img_path)
        coord.append(rx_location)

    print "coord:",coord
    root = Tk()

    #coord = [(2,29),(43,59),(-30,-40),(-60,70),(150,-169)]

    print "===============print point================="
    app = WNFA_GUI(master=root, coord=coord)
    app.master.title("WNFA Final")
    app.mainloop()