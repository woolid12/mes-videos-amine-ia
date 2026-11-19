import json,sys,glob
from rapidocr_onnxruntime import RapidOCR
S=sys.argv[1]; step=int(sys.argv[2])
eng=RapidOCR()
files=sorted(glob.glob(S+'/allf/*.jpg'))
out={}
for i in range(0,len(files),step):
    r,_=eng(files[i])
    out[i]=[[ [list(map(float,p)) for p in b],t,float(c)] for b,t,c in (r or [])]
json.dump(out,open(S+f'/mask/ocr_{step}.json','w'),ensure_ascii=False)
