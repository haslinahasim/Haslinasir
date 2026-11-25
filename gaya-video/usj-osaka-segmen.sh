set -e
ENH="fps=30,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,hqdn3d=1.2:1.2:3:3,unsharp=5:5:0.7,eq=contrast=1.06:saturation=1.12:brightness=0.02,setsar=1,format=yuv420p"
v(){ ffmpeg -loglevel error -y -ss $2 -t $3 -i $1 -an -vf "$ENH" -c:v libx264 -preset veryfast -crf 16 $4; }
p(){ ffmpeg -loglevel error -y -loop 1 -i $1 -an -vf "scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,zoompan=z='1+0.0008*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,eq=contrast=1.04:saturation=1.08,setsar=1,format=yuv420p" -frames:v $(( $2*30/10 )) -c:v libx264 -preset veryfast -crf 16 $3; }
p p_globe.jpg 48 s01.mp4
v c1.mov 0.3 4.4 s02.mp4
v c3.mov 0.0 3.9 s03.mp4
v c4.mov 0.0 4.1 s04.mp4
p p_ninten.jpg 36 s05.mp4
v c5.mov 1.0 4.5 s06.mp4
v c6.mov 1.0 4.0 s07.mp4
v c7.mov 2.0 4.0 s08.mp4
v c8.mov 0.0 4.6 s09.mp4
v c9.mov 1.5 5.0 s10.mp4
v c10.mp4 0.0 3.0 s11.mp4
p p_hogs.jpg 65 s12.mp4
