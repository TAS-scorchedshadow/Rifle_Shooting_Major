var target_details = {"details": ['distance', 'V', '5', '4', '3', '2', '1'],
                      "300m": [300, 70, 140, 280, 420, 600, 1200],
                      "400m": [400, 95, 185, 375, 560, 800, 1800],
                      "500m": [500, 145, 290, 660, 1000, 1320, 1800],
                      "600m": [600, 160, 320, 660, 1000, 1320, 1800],
                      "700m": [700, 255, 510, 815, 1120, 1830, 2400],
                      "800m": [700, 255, 510, 815, 1120, 1830, 2400],
                      "300yds": [274.32, 65, 130, 260, 390, 560],
                      "400yds": [365.76, 85, 175, 350, 520, 745],
                      "500yds": [457.20, 130, 260, 600, 915, 1320],
                      "600yds": [548.64, 145, 290, 600, 915, 1320]
};
//Colors
const targetFill = '#afafaf';
const targetStroke = 'black';

const shotFill = '#afafaf';
const shotStroke = 'black';
const shotText = 'black';

const gridLinesColor = '#7b7b7b';
//c is canvas context objectle
//lineWidth is the thickness of the circle's stroke
function Circle(c, x, y, radius, lineWidth=1) {
    this.lineWidth = lineWidth
    this.x = x;
    this.y = y;
    this.radius = radius;

    this.draw = function() {
        c.beginPath();
        c.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
        c.fillStyle = targetFill;
        c.fill();
        c.lineWidth = this.lineWidth;
        c.strokeStyle = targetStroke;
        c.stroke();
        c.closePath();
        console.log('Drawing circles! :)')
    };
    this.update = function(x=this.x, y=this.y, radius=this.radius, lineWidth=this.lineWidth) {
        this.x = x
        this.y = y
        this.radius = radius
        this.lineWidth = lineWidth

    }
}

//dist is the target distance of the shot
function Target(c, x, y, width, dist){
    this.c = c
    this.dist = dist;
    this.x = x;
    this.y = y;
    this.width = width;
    this.targetCircles = [];
    //Ratio in pixels per millimetre
    this.ratio = this.width/target_details[this.dist][5];
    for (let i=1; i<=5; i++){
        let addCircle = new Circle(this.c, this.x, this.y,target_details[this.dist][i]*this.ratio/2, 1*this.ratio);
        this.targetCircles.push(addCircle);
    }
    this.update = function(x,y,width, ratio) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.ratio = ratio;
        for (let i=0; i<=4; i++){
            this.targetCircles[i].update(this.x, this.y, target_details[this.dist][i+1]*this.ratio/2);
        }
    };
}
//canvasId is the id of the canvas element
//dist is a string that describes the distance of the target eg. "300m"
//width is the width of the target (and height because the target boundaries is a square)
//shots is an array of arrays with the following format:
//[num, x, y]
function DrawTarget(canvasId, dist, shots=[], width='flex'){
    this.init = function() {
        this.canvasObj = document.getElementById(canvasId);
        if (width === 'flex'){
            let rect = this.canvasObj.parentNode.getBoundingClientRect();
            this.canvasObj.width = rect.width;
            this.canvasObj.height = rect.width;

        }
        else{
            this.canvasObj.width = width;
            this.canvasObj.height = width;
        }
        this.x = this.canvasObj.width/2;
        this.y = this.canvasObj.height/2;
        this.dist = dist;
        this.c = this.canvasObj.getContext('2d');
        this.ratio = this.canvasObj.width/target_details[this.dist][5];
        //measurement from https://www.silvermountaintargets.com/uploads/1/1/7/5/117527890/n-icfra-f-australia.tgt
        //it is modified to be in pixels
        this.PX_PER_MOA_PER_1M = (((1.047 * 25.4) / 100) * (39.37 / 36)) * target_details[dist][0] * this.ratio;
        this.target = new Target(this.c, this.x, this.y, this.canvasObj.width, this.dist);

    }

    this.draw = function() {
        // Draw all the circles on the target
        for (let i=4; i>=0; i--) {
            this.target.targetCircles[i].draw()
        }
        // Draw the gridlines of the target, from middle to left/top, then middle to right/bottom
        let xLine = this.x
        let plot_size = this.canvasObj.width
        while (xLine > this.x-plot_size){
            this.c.beginPath();
            this.c.lineWidth = 2 * this.ratio
            this.c.strokeStyle = gridLinesColor;
            this.c.moveTo(xLine, plot_size);
            this.c.lineTo(xLine, -plot_size);
            this.c.stroke();
            this.c.closePath();
            this.c.beginPath();
            this.c.moveTo(plot_size, xLine);
            this.c.lineTo(-plot_size, xLine);
            this.c.stroke();
            this.c.closePath();
            xLine -= this.PX_PER_MOA_PER_1M
        }
        xLine = this.x + this.PX_PER_MOA_PER_1M;
        while (xLine < this.x + this.canvasObj.width/2) {
            this.c.beginPath();
            this.c.lineWidth = 2 * this.ratio
            this.c.strokeStyle = gridLinesColor;
            this.c.moveTo(xLine, plot_size);
            this.c.lineTo(xLine, -plot_size);
            this.c.stroke();
            this.c.closePath();
            this.c.beginPath();
            this.c.moveTo(plot_size, xLine);
            this.c.lineTo(-plot_size, xLine);
            this.c.stroke();
            this.c.closePath();
            xLine += this.PX_PER_MOA_PER_1M
        }
        //Draw indicators for each ring
        for (let i=1; i<=5; i++){
            let indicatorTxt = target_details['details'][i]
            let ringDist = target_details[this.dist][i]/2*this.ratio
            this.c.beginPath();
            this.c.font = "12px Arial";
            this.c.fillStyle= shotText;
            this.c.textAlign = "center";
            this.c.fillText(indicatorTxt, this.x + ringDist-10, this.y-3)
            this.c.closePath();
        }


        //Draw all the individual shots
        let shotsLength = shots.length;
        let shot_x = 0
        let shot_y = 0
        let shot_num = ''
        let font_size = ''
        for (let i=0; i<shotsLength; i++){
            shot_num = shots[i][0];
            shot_x = shots[i][1];
            shot_y = shots[i][2];
            //Draw Circle
            this.c.beginPath();
            this.c.arc(this.x + (shot_x*this.ratio), this.y + (shot_y*this.ratio), 13, 0, Math.PI * 2, false);
            this.c.fillStyle = shotFill;
            this.c.fill();
            this.c.strokeStyle = shotStroke;
            this.c.lineWidth = 1;
            this.c.stroke();
            this.c.closePath();
            //Draw text
            this.c.beginPath();
            this.c.font = "16px Arial";
            this.c.fillStyle= shotText;
            this.c.textAlign = "center";
            this.c.fillText(shot_num, this.x + (shot_x*this.ratio), this.y + (shot_y*this.ratio)+5);
            this.c.closePath();
        }
    }

    this.update = function() {
        if (width === 'flex'){
            let rect = this.canvasObj.parentNode.getBoundingClientRect();
            this.canvasObj.width = rect.width;
            this.canvasObj.height = rect.width;
        }
        this.x = this.canvasObj.width/2
        this.y = this.canvasObj.height/2
        this.ratio = this.canvasObj.width/target_details[this.dist][5];
        //measurement from https://www.silvermountaintargets.com/uploads/1/1/7/5/117527890/n-icfra-f-australia.tgt
        //it is modified to be in pixels
        this.PX_PER_MOA_PER_1M = (((1.047 * 25.4) / 100) * (39.37 / 36)) * target_details[dist][0] * this.ratio;
        //update the target dimensions
        this.target.update(this.x, this.y, this.canvasObj.width, this.ratio)
    };

    this.init();
    this.draw();
    //Change target dimensions if its parent div changes dimensions
    if (width === 'flex'){
        let canvasParent = this.canvasObj.parentNode
        let drawThisTarget = this
        new ResizeSensor(canvasParent, function(){
            drawThisTarget.update();
            drawThisTarget.draw();
        });
    }
}
//
// let canvasParent = document.getElementById(canvasId).parentNode;
// new ResizeSensor(canvasParent, function(){
//
// });


//Unused (might use later)
// function Shot(c, x, y, ratio, num) {
//     this.width = width;
//     this.c = c;
//     this.x = x;
//     this.y = y;
//     this.ratio = ratio;
//     this.draw = function(){
//         //Draw text
//         this.c.font = "30px Arial";
//         this.c.textAlign = "center"
//         this.c.strokeText(num, this.x, this.y);
//         //Draw Circle
//         c.beginPath();
//         c.arc(this.x, this.y, 10*this.ratio, 0, Math.PI * 2, false);
//     }
// }

//c is the canvas context object
//x and y are the coordinates for the centre of the target
//width of the target