Pip installation required:-
pip3 install pillow ,numpy ,mss ,pyobjc
INCASE PILLOW DOESNT WORK AS EXPECTED IN MAC:-
brew install cairo ,libjpeg ,libpng ,freetype
Not sure if these are all that's needed , I just went with the flow , if u get some error , then oops looks like I forgot to install library


Basic explanation on how this code is working:-
First , receiver is run ... then it is listening to any connections made to it's IP address (the receiver's ip address)
Then as soon as the connection is established , the image pixels are sent (depending on what option u choose , whether ur sharing full screen or just some specific application) in the form of bytes i.e. raw data . These raw data being sent is listened and captures and converted back into png format and is shown on the tkinter canvas or whatever u call it

Threads are used for running simultaneous tasks without interrupting anything running in the foreground or background , thts the basic concept of threads , we use it here coz 1. It is a CN project 2. We want to simultaneously send and receive and convert image bytes to image and vice versa  
 

Alos , the sender.py should run only in the macOS platform , and the receiver.py can run in any other os of your choice (tested in macOS and ubuntu , so im assuming windows shd work)

The sender.py uses a macOS specific library which is called quartz (better not to tell this shit and all , just tell tkinter gui im using) 

The cn concepts u using here is socket programming :-

Thingys to remember in Sender.py

Wherever u use sock as the prefix of a function like sock.connect(1arg,2arg) , sock.bind() etc
Import socket is the socket programming ka import function
TCP connection is established via SOCK_STREAM (it's only in the sender.py file) , final tcp connection is made whn using the sock.connect(ip , port_num)

One more thing , sock is the sock object which is created as soon as u import the socket library 
sock=socket.socket() ---> sock is the socket object created 



Thingys to remember in Receiver.py 

sock.bind(host , port) is just listening all the connections on this specific IP address of the host and port
So the bind() attaches the socket to the specific ip and port
self.server.bind((host, 9999)). (In the host part , ur ip address which u enter in gui gets filled)
This machine is the server. I’m now listening for connections on all network interfaces on port 9999


You are also using the concept of data serialization and transmission :-
See the thing is ur not actually sharing ur screen , ur are sending live transmissions of image chunks (pixels) in the network and hosting it

Thingys to remember in Sender.py
Ur converting the data obtained to png format and then extracts the raw data (image bytes/pixels) from the memory buffer . Then calculates how many bytes is to be sent and sends it over the socket

Thingys to remember in receiver.py
It reads the bytes to determine how big the image is going to be and then converts those bytes to actual integers , then with that value , it converts the raw bytes back into a PIL.Image object(PIL is that pillow thingy we are importing) pillow is just an image library in python that's it , it helps in doing stuff with images . In this code , it helped in creating image frm pixels , then saving it to a buffer to transfer it and then in receiver.py , it converts the bytes back to image . 
In one line , pillow helps in encoding and decoding png format 

 



