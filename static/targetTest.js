canvas = document.getElementById('title');
console.log('hello');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

var c = canvas.getContext('2d');
//just trying out canvas currently doesn't make a target but a colorful pattern
let x = 0
let y = 0
maxWidth = window.innerWidth
maxHeight = window.innerHeight
while (y <= maxHeight) {
    while (x <= maxWidth) {
        c.beginPath();
        let green = Math.floor(Math.random() * 255).toString();
        let blue = Math.floor(Math.random() * 255).toString();
        let red = Math.floor(Math.random() * 255).toString();
        let rgbString = 'rgb(' + red + ',' + green + ',' + blue + ')';
        c.strokeStyle = rgbString;
        c.arc(x, y, 100, 0, Math.PI * 2, false);
        c.fillStyle = rgbString;
        c.fill();
        c.stroke();
        x += 50;
    }
    y += 50
    x = 0
}
