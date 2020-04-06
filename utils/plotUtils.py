import numpy as np
import datetime

def gradientbars(bars, ax, maxheight):
    
    grad = np.atleast_2d(np.linspace(0,1,256)).T
    residual_grad=np.ones(shape=grad.shape)
    lim = ax.get_xlim()+ax.get_ylim()
    for bar in bars:
        bar.set_zorder(1)
        bar.set_facecolor("none")
        x,y = bar.get_xy()
        w, h = bar.get_width(), bar.get_height()
        ax.imshow(grad, extent=[x,x+w,y,y+h], aspect="auto", cmap='gray_r', zorder=0, alpha=1)
        ax.imshow(residual_grad, extent=[x,x+w,y+h, maxheight+20], aspect="auto", cmap='gray_r', alpha=.3, zorder=0)
        
    ax.axis(lim)
    
def getTimeNum(integer):
    
    return datetime.datetime(1900, 1, 1, integer)