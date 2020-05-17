from PIL import Image

basewidth = 100;
img = Image.open('playerTank.png')
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize), Image.ANTIALIAS)

for i in range(0, 36):
    im2 = img.rotate(i*10);
    im2.save('playerRotated/' + str(i) + '.png');
print("end");
