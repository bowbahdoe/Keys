#PyJ2D - Copyright (C) 2011 James Garnon

from __future__ import division
from javax.imageio import ImageIO
from java.io import File
from surface import Surface
import env
from java.io import InputStream
__docformat__ = 'restructuredtext'
from java.lang import ClassLoader

class Image(object):
    """
    **pyj2d.image**
    
    * pyj2d.image.load
    """

    def __init__(self):
        """
        Initialize Image module.
        
        Module initialization creates pyj2d.image instance.
        """
        pass

    def load(self, img_file, namehint=None):
        """
        Load image from file as a java.awt.image.BufferedImage.
        Return the bufferedimage as a Surface.
        """
        try:
            try:
                f = env.japplet.class.getResource(img_file.replace('\\','/'))    #java uses /, not os.path Windows \
                if not f:
                    raise
            except:
                cload = ClassLoader.getSystemClassLoader()
                f = cload.getResourceAsStream(img_file.replace('\\','/'))
                print "fe"
                
        except:
            
            f = File(img_file)
        
        bimage = ImageIO.read(f)
        surf = Surface(bimage)
        return surf

