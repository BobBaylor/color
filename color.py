#! /usr/bin/env python 

useStr = """
 --Display random glass placement--
 Usage:
  color  [--weights=<W>] [--test] [--length=<L>] [--position=<P>] [--background=<B>] [--show=<S>]
  color -t | --test
  color -h | --help
  color -v | --version

 Options:
  -b --background <B>     Background color [default: 200,200,200]
  -h --help               Show this screen.
  -l --length <L>         Random length factor [default: 0.4]
  -p --position <P>       Random x,y placement [default: 2,2]
  -s --show <S>           True to display result on screen [default: True]
  -t --test               Run internal tests.
  -v --version            show the version
  -w --weights <W>        percent each color in alpha order [default: 20,20,20,20,20,20].
    """

import docopt

import os
import sys
import random
# import readline as rdln
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont



def addTile(pos,imout,r,cutX,rp):
    rgn = r
    pos = (pos[0]+random.randint(0,rp[0]),pos[1]+random.randint(0,rp[1]))
    if cutX:
        rgn = rgn.crop((0,0,rgn.size[0]-cutX,rgn.size[1]))
    wid = rgn.size[0]
    if wid + pos[0] < imout.size[0]:
        imout.paste(rgn,(pos[0],pos[1],pos[0]+rgn.size[0],pos[1]+rgn.size[1]))
    return wid


# ----- bag is filled with (probaly) enough tiles to fill the canvas and removed at random ----------
tileBag = []

def pickTile():                             # return a random tile from the bag
    i = random.randint(0,len(tileBag)-1)    # this might fail - caller should catch ValueError exception
    return tileBag.pop(i)


def fillTileBag(weights,imoutSize,tileSize,shortenFactor):
    global tileBag
    cnt = (1.0/(1.0-shortenFactor*0.5))*(imoutSize[0]/tileSize[0])
    cnt = cnt*                          (imoutSize[1]/tileSize[1])
    scl = 1.0+cnt/float(sum(weights))
    #    print cnt, scl
    for i,c in enumerate(weights):
        tileBag = tileBag+[i]*int(c*scl)


# not used
def weighted_choice(weights):
   total = sum(weights)
   r = random.uniform(0, total)
   upto = 0
   for i, w in enumerate(weights):
      if upto + w >= r:
         return i
      upto += w
   assert False, "Shouldn't get here"




gfNamelst = [
    'glassGold1.jpg',
    'glassGold2.jpg',
    'glassGreen1.jpg',
    'glassGreen2.jpg',
    'glassGreen3.jpg',
    'glassWhite.jpg', ]



def getTileImages():
    imgs = []
    imgMins = [10000,10000]
    for fn in gfNamelst:    # os.listdir( '.' ):     # get the glass samples and find the largest size that they can all handle
        if 'glass' in fn:
            imgs += [Image.open(fn)]
            for i in range(2):
                if  imgMins[i] > imgs[-1].size[i]:
                    imgMins[i] = imgs[-1].size[i]
    box = (0,0,imgMins[0],imgMins[1])
    # print 'using glass dimensions of',box
    rTiles = [ im.crop(box) for im in imgs ]   # crop the glass samples to a consistent size
    return rTiles, imgMins



def genGlass( opts ):
    clrBg = tuple([int(v.strip()) for v in opts['--background'].split(',')])     # get a triplette of the background color
    
    if ',' in opts['--weights']:
        weights = [int(v.strip()) for v in opts['--weights'].split(',')]     # get a list of the tile color weights
    elif '_' in opts['--weights']:
        weights = [int(v.strip()) for v in opts['--weights'].split('_')]     # get a list of the tile color weights
    else:
        weights = [int(v.strip()) for v in opts['--weights'].split(' ')]     # get a list of the tile color weights

    randPos = [int(v.strip()) for v in opts['--position'].split(',')]    # get a list of the x,y random pixel variation
    shortenFactor = float(opts['--length'])                              # tiles can be up to X times shorter than the samples
    bDoShow = True if 't' in opts['--show'].lower() else False

    if opts['--test']:
        print opts

    legend = ''.join( ['\n%2d of %s'% (a[0],a[1]) for a in zip(weights,gfNamelst)])
    # print legend

    rTiles, imgMins = getTileImages()
    # box = (0,0,imgMins[0],imgMins[1])

    marg = 30
    imc = Image.new('RGB',(imgMins[0]+marg*2,imgMins[1]*len(rTiles)+marg*2))
    dctxt = ImageDraw.Draw(imc)
    try:
        fnt = ImageFont.truetype('couri.ttf',40)
        # fnt = ImageFont.truetype('aller-bold.ttf',40)
    except IOError:
        # print 'using default font'
        fnt = ImageFont.load_default()

    for i, r in enumerate(rTiles):         # make a legend with text showing glass file and weight
        imc.paste(r,(marg,marg+imgMins[1]*i,marg+imgMins[0],marg+imgMins[1]*(i+1)))
        dctxt.text((marg,marg+imgMins[1]*i), '%2d of %s'% (weights[i],gfNamelst[i]),(0,0,0))
    if not bDoShow:
        imc.show()

    """
    imb = Image.new('RGB',(400,400))
    imb.putdata([(100,200,100)]*400*400)
    fnt = ImageFont.truetype('couri.ttf',20)
    fnt = ImageFont.load_default()
    d = ImageDraw.Draw(imb)
    d.text((15,60),'oops!',font=fnt)
    imb.show()
    """
    imout = Image.new('RGB',(5400,2400))

    fillTileBag(weights,imout.size,imgMins,shortenFactor)
    cntTotalTiles = len(tileBag)
    imout.putdata( [clrBg]*imout.size[0]*imout.size[1] )   # light gray background
    dUsed = [0]*len(rTiles)
    # for r in range(imout.size[1]/box[3]):
    row = 0
    bRowsRemain = True
    while bRowsRemain:
        col = 0
        while True:
            # iTile = weighted_choice(weights)
            try:
                iTile = pickTile()
            except ValueError:
                if opts['--test']:
                    print 'Ran out of tiles at',row,col
                bRowsRemain = False
                break
            dUsed[iTile] = dUsed[iTile]+1
            shortenX = int(random.random()*imgMins[0]*shortenFactor)           # add variable length
            t = rTiles[iTile]
            if random.choice([True,False]):
                t = t.transpose(Image.FLIP_LEFT_RIGHT)
            if random.choice([True,False]):
                t = t.transpose(Image.FLIP_TOP_BOTTOM)
            col += addTile((col,row),imout,t,shortenX,randPos)  # todo: leave a little space

            if col >= imout.size[0]:
                break
        row += imgMins[1]
        if row+imgMins[1]+randPos[1] > imout.size[1]:
            bRowsRemain = False

    frame = (int(imgMins[0]*.3),0,int(imout.size[0]-imgMins[0]*.8),imout.size[1])    # trim it left and right
    imout = imout.crop(frame)
    imout.paste(imc,(0,0,imc.size[0],imc.size[1]))

    foname = 'color'+'_%02d'*len(weights)+'.jpg'
    imout.save(foname%tuple(weights))
    # imout.save(os.path.join('out',foname%tuple(weights)))

    if bDoShow:
        imout.show()

    # test the distribution of tiles
    tScale = sum(weights)*1.0/sum(dUsed)
    tChoice = ''.join( ['%.1f, '% (tScale*a[1]) for a in zip(weights,dUsed)])
    if opts['--test']:
        print len(tileBag),'tiles of',cntTotalTiles,'remain.',
        print 'Actual weights:',tChoice[:-2]



if __name__ == '__main__':
    opts = docopt.docopt(useStr,version='0.0.2')
    genGlass( opts )


