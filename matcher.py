from pathlib import Path
import cv2
import numpy as np

IMAGE_EXTENSIONS = {".jpg",".jpeg",".png",".bmp",".webp"}

class ImageMatcher:
    """
    Hybrid visual matcher:
      1. ORB local feature matching for shape/details.
      2. HSV histogram similarity for overall color distribution.
    The final score is a ranking score, NOT a probability.
    """

    def __init__(self, orb_features=2500):
        self.orb = cv2.ORB_create(nfeatures=orb_features)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    @staticmethod
    def read(path):
        img = cv2.imread(str(path))
        return img

    @staticmethod
    def histogram(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0,1], None, [32,32], [0,180,0,256])
        cv2.normalize(hist, hist)
        return hist

    def _orb_score(self, a, b):
        a = cv2.resize(a, (700,700))
        b = cv2.resize(b, (700,700))
        ga = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
        gb = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
        k1,d1 = self.orb.detectAndCompute(ga, None)
        k2,d2 = self.orb.detectAndCompute(gb, None)
        if d1 is None or d2 is None or len(d1)<2 or len(d2)<2:
            return 0.0, 0
        pairs = self.matcher.knnMatch(d1,d2,k=2)
        good=[]
        for pair in pairs:
            if len(pair)!=2: continue
            m,n=pair
            if m.distance < 0.75*n.distance:
                good.append(m)
        # Saturating function makes the score less sensitive to image size.
        score = 100.0 * (1.0 - np.exp(-len(good)/35.0))
        return float(min(score,100.0)), len(good)

    def _color_score(self, a, b):
        ha,hb=self.histogram(a),self.histogram(b)
        corr=cv2.compareHist(ha,hb,cv2.HISTCMP_CORREL)
        return float(np.clip((corr+1)*50,0,100))

    def compare(self, query_path, candidate_path):
        a=self.read(query_path); b=self.read(candidate_path)
        if a is None or b is None:
            return {"score":0.0,"orb":0.0,"color":0.0,"good_matches":0}
        orb,good=self._orb_score(a,b)
        color=self._color_score(a,b)
        final=(orb*0.75)+(color*0.25)
        return {"score":round(float(final),2),"orb":round(orb,2),
                "color":round(color,2),"good_matches":good}

    def rank(self, query_path, candidate_paths, top_n=5):
        results=[]
        for path in candidate_paths:
            try:
                metrics=self.compare(query_path,path)
                results.append((metrics["score"],Path(path),metrics))
            except Exception:
                continue
        results.sort(key=lambda x:x[0], reverse=True)
        return results[:top_n]

def confidence(score):
    if score >= 70: return "HIGH"
    if score >= 45: return "MEDIUM"
    return "LOW"
