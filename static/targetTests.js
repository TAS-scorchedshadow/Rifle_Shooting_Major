// canvas = document.getElementById('title');
// console.log('hello');
// canvas.width = 400;
// canvas.height = 400;
// var c = canvas.getContext('2d');
// //just trying out canvas currently doesn't make a target but a zoomable circle
maxWidth = window.innerWidth;
maxHeight = window.innerHeight;
var target_details = {"300m": [300, 70, 140, 280, 420, 600],
                      "400m": [400, 95, 185, 375, 560, 800],
                      "500m": [500, 145, 290, 660, 1000, 1320],
                      "600m": [600, 160, 320, 660, 1000, 1320],
                      "700m": [700, 255, 510, 815, 1120, 1830],
                      "800m": [700, 255, 510, 815, 1120, 1830],
                      "300yds": [274.32, 65, 130, 260, 390, 560],
                      "400yds": [365.76, 85, 175, 350, 520, 745],
                      "500yds": [457.20, 130, 260, 600, 915, 1320],
                      "600yds": [548.64, 145, 290, 600, 915, 1320]};
// let x = 0;
// let y = 0;
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
// window.addEventListener('mousewheel', function(event) {
//     let change = event.deltaY * -0.1;
//     let circle1 = circleArray[2];
//     console.log(circle1);
//     if (Math.abs(event.x - circle1.x) < circle1.radius && Math.abs(event.y - circle1.y) < circle1.radius){
//         if (circle1.radius + change > 100 && circle1.radius + change < 300) {
//             for (let i=0; i < 3; i++) {
//                 circleArray[i].radius += change
//             }
//
//         }
//         document.body.style.overflow = 'hidden';
//     }
//     else {
//         document.body.style.overflow = 'auto';
//     }
// })


function Circle(c, x, y, radius) {
    this.x = x;
    this.y = y;
    this.radius = radius;
    this.draw = function() {
        c.beginPath();
        c.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
        c.fillStyle = '#76ce76';
        c.fill();
        c.stroke();
    };
    this.update = function() {
        this.draw();
    }
}

function Target(c, x, y, width, dist){
    this.dist = dist;
    this.x = x;
    this.y = y;
    this.width = width;
    this.targetCircles = [];
    this.ratio = this.width/target_details[this.dist][5];
    console.log(this.width);
    for (let i=1; i<=5; i++){
        let addCircle = new Circle(c, this.x, this.y,target_details[this.dist][i]*this.ratio);
        this.targetCircles.push(addCircle);
    }
}

function DrawTarget(canvasId, x, y, dist, width){
    this.canvasObj = document.getElementById(canvasId);
    this.canvasObj.width = width;
    this.canvasObj.height = width;
    this.x = x;
    this.y = y;
    this.dist = dist;
    this.c = this.canvasObj.getContext('2d');
    this.target = new Target(this.c, this.x, this.y, this.canvasObj.width/2, this.dist);
    this.draw = function() {
        for (let i=4; i>=0; i--) {
            this.target.targetCircles[i].draw()
        }
    }
}

let myTarget = new DrawTarget('title', canvas.width/2, canvas.height/2, "300m", 400);
myTarget.draw();
console.log(myTarget);