canvas = document.getElementById('title');
console.log('hello');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
var c = canvas.getContext('2d');
// //just trying out canvas currently doesn't make a target but a zoomable circle
// let x = 0
// let y = 0
maxWidth = window.innerWidth
maxHeight = window.innerHeight
// while (y <= maxHeight) {
//     while (x <= maxWidth) {
//         c.beginPath();
//         let green = Math.floor(Math.random() * 255).toString();
//         let blue = Math.floor(Math.random() * 255).toString();
//         let red = Math.floor(Math.random() * 255).toString();
//         let rgbString = 'rgb(' + red + ',' + green + ',' + blue + ')';
//         c.strokeStyle = rgbString;
//         c.arc(x, y, 80, 0, Math.PI * 2, false);
//         c.fillStyle = rgbString;
//         c.fill();
//         c.stroke();
//         x += 100;
//     }
//     y += 100
//     x = 0
// }
window.addEventListener('mousewheel', function(event) {
    let change = event.deltaY * -0.1;
    let circle1 = circleArray[2];
    console.log(circle1);
    if (Math.abs(event.x - circle1.x) < circle1.radius && Math.abs(event.y - circle1.y) < circle1.radius){
        if (circle1.radius + change > 100 && circle1.radius + change < 300) {
            for (let i=0; i < 3; i++) {
                circleArray[i].radius += change
            }

        }
        document.body.style.overflow = 'hidden';
    }
    else {
        document.body.style.overflow = 'auto';
    }
})


function Circle(x,y, radius) {
    this.x = x
    this.y = y
    this.radius = radius
    this.draw = function() {
        c.beginPath();
        c.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
        c.fillStyle = '#76ce76';
        c.fill();
        c.stroke();
    }
    this.update = function() {
        this.draw();
    }
}
var circleArray = [];
for (let i = 0; i < 3; i++){
    circleArray.push(new Circle(maxWidth/2, maxHeight/2, (3-i)*100))
}
function animate(){
    requestAnimationFrame(animate);
    c.clearRect(0,0, maxWidth, maxHeight)
    for (let i = 0; i < 3; i++){
        circleArray[i].update()
    }
}
animate();