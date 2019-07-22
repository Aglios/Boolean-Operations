import matplotlib.pyplot as plt
from .bundle import Bundle
#BundleList itself holds red bundles
#case0: botHi>topLo and botHi>topHi
#case1: botHi>topLo and botHi<topHi
#case2: botHi<topLo
class BundleList:
    def __init__(self,rang): # blue over red
        redMin=Bundle.fromCoord(-rang,-rang,rang,-rang,0)
        
        blueMin=Bundle.fromCoord(-rang,-rang,rang,-rang,1)
        blueMin.bel=redMin
        redMin.abv=blueMin
        
        redMax=Bundle.fromCoord(-rang,rang,rang,rang,0)
        redMax.bel=blueMin
        blueMin.abv=redMax
        
        blueMax=Bundle.fromCoord(-rang,rang,rang,rang,1)
        blueMax.bel=redMax
        redMax.abv=blueMax
        
        
        self.lowest=redMin
        self.highest=blueMax
    
    def plot(self):
        color=1
        cur=self.highest
        while cur!=None:
#            assert cur.color==color
            cur.plot()
            color = 1-color
            cur=cur.bel
        plt.show()
        
    #input:segment,bundle A it is being inserted after
    #output: add the segment as bundle B after bundle A
    def segBundle(self,seg,A):
        #A<B<C
        C=A.abv
        B=Bundle.fromSeg(seg,A,C)
        A.abv=B    
        C.bel=B
        assert A.color!=B.color and B.color!=C.color
        return B
    
    #input: flag, bundle, direc direction to include (1 includes up, 0 includes down)
    #output: splits the tree at the flag, maintains abv and bel bundles
    #will temporarily break bundleList color invariant
    def split(self,flag,bundle,direc):
        #bot<bundle<top to bot<bundle<B<top
        top=bundle.abv
        [node,d]=bundle.flagTest(flag)
#        print('splitting',d)
        if d==-1:
            node=node.predecessor()
            [t1,t2]=bundle.split(node.seg) #dispatch to bundle
        elif d==1:
            [t1,t2]=bundle.split(node.seg)
        else:
            if bundle.tree.root.left==None and bundle.tree.root.right==None:
                return [bundle,bundle]
            elif direc==1:
                node=node.predecessor()
                [t1,t2]=bundle.split(node.seg)
            else:
                [t1,t2]=bundle.split(node.seg)
        #bundle set to the lower split
        if t2==None:
            B=Bundle()
        else:
            B=Bundle(t2,bundle,top)
            bundle.tree=t1
            bundle.abv=B
            top.bel=B
        return [bundle,B]
    
    #input: bundle A
    #output: if of same color: A joined with one above, the one above's fields are set to None
            #else do nothing
    #only need to worry about losing topLo
    def join(self,A):
        #bot<A<B<top to bot<A<top
        assert A.abv!=None
        if A.color!=A.abv.color:
#            print ("Error: attempted join of opposite colors")
            return A
        print("join")
        B=A.abv
        top=B.abv
        A=A.join(B)
        
        A.abv=top
        top.bel=A
        return A
    
    #input: segment and bundle
    #output: deletes seg from bundle. if the bundle becomes empty, remove it from the list
    def delete(self,seg,bundle):
        print("delete")
        bot=bundle.bel
        top=bundle.abv
        bundle=bundle.delete(seg)
        if bundle.isEmpty():
            bot.abv=top
            top.bel=bot
            self.join(bot)
        return bundle
    
    #input:bundle A
    #output:swap A with the one above. Join if necessary
    #yet to report intersections
    def swap(self,A):
        #bot<A<B<top to bot<B<A<top
        B=A.abv
        print(A.size()*B.size(), "intersections")
        bot=A.bel
        top=B.abv
        
        bot.abv=B
        B.bel=bot
        
        B.abv=A
        A.bel=B
        
        A.abv=top
        top.bel=A
        
        self.join(bot)
        self.join(A)
        return A
    
    #input: flag,start bundle
    #output: bundle(with the same color as start bundle) directly below the flag or the bundle encompassing it
    def findFlag(self,flag,start):
        cur=start
        #invariant: cur is a bundle(same color as start) that's below or contains the flag
        while cur.abv.abv!=None and flag.cmpSeg(cur.abv.abv.min())>=0:
            cur=cur.abv.abv
        return cur
    
    #input:flag, bundle containing or directly below the flag, position of bundle(higher one 1 or lower one 0)
    #output:the bundles directly above and below the flag
    def flagLoHi(self,flag,bundle,pos):
        if flag.cmpSeg(bundle.max())>0:
            return [bundle,bundle.abv.abv]
        elif pos==0:
            [lo,hi]=self.split(flag,bundle,1)
        else:
            [lo,hi]=self.split(flag,bundle,0)
        return [lo,hi]

    #input:flag
    #output: [botLo,botHi,topLo,topHi]
    def findLoHi(self,flag):
        red=self.findFlag(flag,self.lowest)
        blue=self.findFlag(flag,self.lowest.abv)
        if red>blue:
            [botLo,botHi]=self.flagLoHi(flag,blue,0)
            [topLo,topHi]=self.flagLoHi(flag,red,1)
        else:
            [botLo,botHi]=self.flagLoHi(flag,red,0)
            [topLo,topHi]=self.flagLoHi(flag,blue,1)
        return [botLo,botHi,topLo,topHi]
    
    #input: flag
    #output: returns 0 for case0, 1 for case1 described above
    def checkCase(self,botLo,botHi,topLo,topHi):
        if botHi>topLo:
            if botHi>topHi:
                return 0
            else:
                return 1
        else:
            assert botHi<topLo
            return 2
    
    #input:botHi,topLo where botHi<topLo
    #output:swap botHi until botHi>topLo
    def swapBotHi(self,botHi,topLo):
        assert botHi<topLo
        while botHi.abv.abv<topLo:
            botHi=self.swap(botHi)
        #swap botHi but still keeping topLo (else topLo will be lost in the swap)
        botHi=self.swap(botHi)
        topLo=botHi.bel #SM: why does this not give topLo.abv==botHi
        assert not topLo.isEmpty()
        assert topLo.abv==botHi
        assert topLo==botHi.bel
        return [botHi,topLo]
    
    #input: start flag, topLo
    #output: adds the flag.seg while maintaining invariant
    def procStart0(self,flag,topLo,topHi):
        if flag.seg.color==topLo.color:
            topHi=topLo
            self.join(topLo)
            topLo.insert(flag.seg)
            return topLo
        else:
            return self.segBundle(flag.seg,topLo)
    
    #input: start flag, botHi, topLo
    #output: adds segment of flag into the corresponding bundle and returns the bundle
    def procStart1(self,flag,botHi,topLo):
        if flag.seg.color==botHi.color:
            botHi.insert(flag.seg)
            return botHi
        else:
            topLo.insert(flag.seg)
            return topLo
    
    #input: end flag,botHi bundle, topLo bundle
    #output: removes the segment of the flag from the corresponding bundle and returns the bundle
    def procEnd(self,flag,botHi,topLo,topHi):
        if topLo.abv==topHi:
            topHi=topLo
            self.join(topLo)
        if flag.seg.color==botHi.color:
            assert botHi.contains(flag.seg)
            self.delete(flag.seg,botHi)
            return botHi
        else:
            assert flag.seg.color==topLo.color
            assert topLo.contains(flag.seg)
            self.delete(flag.seg,topLo)
            return topLo
    
    #input: flag
    #output: process the flag for sweep line, returns the bundle where the seg is added/removed
    def procFlag(self,flag):
        [botLo,botHi,topLo,topHi]=self.findLoHi(flag)
        if topHi.isEmpty():
            topHi=topLo
#            print("empty split")
        case=self.checkCase(botLo,botHi,topLo,topHi)
        print('case',case)
        if case==0:
            if flag.type==0:
                return self.procStart0(flag,topLo,topHi)
            else:
                return self.procEnd(flag,botHi,topLo,topHi)
        elif case==1:
            if flag.type==0:
                return self.procStart1(flag,botHi,topLo)
            else:
                return self.procEnd(flag,botHi,topLo,topHi)
        else:
            [botHi,topLo]=self.swapBotHi(botHi,topLo)
            assert self.checkCase(botLo,botHi,topLo,topHi)==1
            if flag.type==0:
                return self.procStart1(flag,botHi,topLo)
            else:
                return self.procEnd(flag,botHi,topLo,topHi)