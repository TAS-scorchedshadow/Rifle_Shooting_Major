//By Henry Guo
var target_details = {
    "details": ['V', '5', '4', '3', '2', '1'],
    "300m": [300, 70, 140, 280, 420, 600, 1200],
    "400m": [400, 95, 185, 375, 560, 800, 1800],
    "500m": [500, 145, 290, 660, 1000, 1320, 1800],
    "600m": [600, 160, 320, 660, 1000, 1320, 1800],
    "700m": [700, 255, 510, 815, 1120, 1830, 2400],
    "800m": [700, 255, 510, 815, 1120, 1830, 2400],
    "274m": [274.32, 65, 130, 260, 390, 560],
    "365m": [365.76, 85, 175, 350, 520, 745],
    "457m": [457.20, 130, 260, 600, 915, 1320],
    "548m": [548.64, 145, 290, 600, 915, 1320]
};
//Colors
var targetFill = '#afafaf';
var targetStroke = 'black';
var groupColours = ['red', 'blue', 'green', 'yellow', 'brown']
var shotFill = '#afafaf';
var shotStroke = 'black';
var shotText = 'black';

var gridLinesColor = '#7b7b7b';

function Circle(c, x, y, radius, fillColor='white', strokeColor='black', lineWidth=1) {
    /**
     * Draws a circle.
     *
     * @param The canvas.context object
     * @param x The circle centre's x-coordinate in pixels, respective to the origin of the canvas element
     * @param y The circle centre's y-coordinate in pixels, respective to the origin of the canvas element
     * @param radius The radius of the circle
     * @param fillColor A hex string which is the fill color of the circle
     * @param strokeColor A hex string which is the color of the circle border
     * @param lineWidth thickness of the circle border
     */
    this.dpr = Math.ceil(window.devicePixelRatio);
    this.lineWidth = lineWidth*this.dpr;
    this.x = x;
    this.y = y;
    this.radius = radius;

    this.draw = function() {
        /**
         * function draws the circle on the given canvas object
         */
        c.beginPath();
        //Draw circle
        c.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
        //Fill the circle with the set color
        c.fillStyle = fillColor;
        c.fill();
        //Draw the border, if lineWidth is 0 don't draw the border
        c.lineWidth = this.lineWidth;
        if (this.lineWidth > 0){
            c.strokeStyle = strokeColor;
            c.stroke();
        }
        c.closePath();
    };
    this.update = function(x=this.x, y=this.y, radius=this.radius, lineWidth=this.lineWidth) {
        /**
         * Updates the values of this object to the parameters
         *
         * @param c The canvas.context object
         * @param x The circle centre's x-coordinate respective to the origin of the canvas element
         * @param y The circle centre's y-coordinate respective to the origin of the canvas element
         * @param radius The radius of the circle
         * @param lineWidth The width of the circle border
         */
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.lineWidth = lineWidth

    }
}

//dist is the target distance of the shot
function Target(c, x, y, width, dist){
    /**
     * @param c the canvas.context object
     * @param x the circle centre's x-coordinate respective to the origin of the canvas element
     * @param y the circle centre's y-coordinate respective to the origin of the canvas element
     * @param width the width (in pixels) of the canvas object
     * @param dist the distance of the target e.g 300m
     */
    this.c = c;
    this.dist = dist;
    this.x = x;
    this.y = y;
    this.width = width;
    this.targetCircles = [];
    //Ratio in pixels per millimetre
    this.ratio = this.width/target_details[this.dist][5];
    for (let i=1; i<=5; i++){
        let addCircle = new Circle(this.c, this.x, this.y,target_details[this.dist][i]*this.ratio/2, targetFill, targetStroke, 1*this.ratio);
        this.targetCircles.push(addCircle);
    }
    this.update = function(x,y,width, ratio) {
        /**
        * @param x The circle centre's x-coordinate respective to the origin of the canvas element
        * @param y The circle centre's y-coordinate respective to the origin of the canvas element
        * @param width The width (in pixels) of the canvas object
        * @param ratio The drawing ratio (defined as width of canvas object divided by radius of outer circle)
        */
        this.x = x;
        this.y = y;
        this.width = width;
        this.ratio = ratio;
        for (let i=0; i<=4; i++){
            this.targetCircles[i].update(this.x, this.y, target_details[this.dist][i+1]*this.ratio/2);
        }
    };
}

function DrawTarget(canvasId, dist, shots=[], groupCircle=null, width='flex'){
    /**
     * @param canvasId the id attribute of the canvas object which the target would be drawn on
     * @param dist distance of the target e.g 300m
     * @param shots an array of arrays with the following format: [num, x, y, score]
     * @param width is width of the canvas object
     */
    //Initialise all the variables
    this.init = function() {
        //collect canvasObj
        this.canvasObj = document.getElementById(canvasId);
        /**
        Following line gets the device pixel ratio
        The device pixel ratio is how the screen scales each pixel
        For example. on an iPhoneX, it has a device pixel ratio of 3, so when drawing a line of size 6px,
        the screen will render it as 2px but still draw it at a size of 6px causing pixellation.
        For more details see https://dev.to/pahund/how-to-fix-blurry-text-on-html-canvases-on-mobile-phones-3iep
        */
        this.dpr = Math.ceil(window.devicePixelRatio);
        let parentWidth = $("#" + canvasId).parent().width();
        /**
        Code borrowed from https://dev.to/pahund/how-to-fix-blurry-text-on-html-canvases-on-mobile-phones-3iep
        The code makes the canvas obj draw at double the size
        Then we scale the obj down with css so that it appears the same size
        More in-depth explanation can be found in above website
         */
        if (width === 'flex'){
            this.canvasObj.width = parentWidth*this.dpr;
            this.canvasObj.height = parentWidth*this.dpr;
            this.canvasObj.style.width = parentWidth + 'px';
            this.canvasObj.style.height = parentWidth + 'px';
        } else {
            this.canvasObj.width = width*this.dpr;
            this.canvasObj.height = width*this.dpr;
            this.canvasObj.style.width = width + 'px';
            this.canvasObj.style.height = width + 'px';
        }

        //Set the centre coordinates of the target
        this.x = this.canvasObj.width/2;
        this.y = this.canvasObj.height/2;
        //Set the distance
        this.dist = dist;
        //Set the canvas context object
        this.c = this.canvasObj.getContext('2d');
        //Radius of the individual shots
        this.shotRadius = 13*this.dpr;
        //Ratio is defined so that the shots and other stuff drawn will be scaled correctly within the canvas obj
        this.ratio = this.canvasObj.width/target_details[this.dist][5];

        //measurement from https://www.silvermountaintargets.com/uploads/1/1/7/5/117527890/n-icfra-f-australia.tgt
        //it is modified to be in pixels
        this.PX_PER_MOA_PER_1M = (((1.047 * 25.4) / 100) * (39.37 / 36)) * target_details[this.dist][0] * this.ratio;
        this.target = new Target(this.c, this.x, this.y, this.canvasObj.width, this.dist);

        //grouping circle dimensions
        if (groupCircle) {
            this.grouping = []
            for (let i=0; i<groupCircle.length; i++){
                console.log(groupCircle)
                this.grouping.push({'x': this.x + groupCircle[i][0]*this.ratio, 'y': this.y - groupCircle[i][1]*this.ratio, 'r': groupCircle[i][2]*this.ratio/2})
            }
        }

    };
    //this.update updates all the values in DrawTarget object after it changes sizes
    this.update = function() {
        this.dpr = Math.ceil(window.devicePixelRatio);
        if (width === 'flex'){
            let parentWidth = $("#" + canvasId).parent().width();
            this.canvasObj.width = parentWidth*this.dpr;
            this.canvasObj.height = parentWidth*this.dpr;
            this.canvasObj.style.width = parentWidth + 'px';
            this.canvasObj.style.height = parentWidth + 'px';
        }
        this.x = this.canvasObj.width/2;
        this.y = this.canvasObj.height/2;
        this.ratio = this.canvasObj.width/target_details[this.dist][5];
        //measurement from https://www.silvermountaintargets.com/uploads/1/1/7/5/117527890/n-icfra-f-australia.tgt
        //it is modified to be in pixels
        this.PX_PER_MOA_PER_1M = (((1.047 * 25.4) / 100) * (39.37 / 36)) * target_details[this.dist][0] * this.ratio;
        //update the target dimensions
        this.target.update(this.x, this.y, this.canvasObj.width, this.ratio);
    };

    this.draw = function() {
        // Draw all the score rings on the target
        for (let i=4; i>=0; i--) {
            this.target.targetCircles[i].draw();
        }
        // Draw the grid-lines of the target, from middle to left/top, then middle to right/bottom
        let xLine = this.x;
        let plot_size = this.canvasObj.width;
        while (xLine > this.x-plot_size){
            this.c.beginPath();
            this.c.lineWidth = 2 * this.ratio;
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
            xLine -= this.PX_PER_MOA_PER_1M;
        }
        xLine = this.x + this.PX_PER_MOA_PER_1M;
        while (xLine < this.x + this.canvasObj.width/2) {
            this.c.beginPath();
            this.c.lineWidth = 2 * this.ratio;
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
            xLine += this.PX_PER_MOA_PER_1M;
        }
        //Draw indicators for each ring
        for (let i=0; i<=4; i++){
            let indicatorTxt = target_details['details'][i];
            let ringDist = target_details[this.dist][i+1]/2*this.ratio;
            this.c.beginPath();
            this.c.font = "12px Arial";
            this.c.fillStyle= shotText;
            this.c.textAlign = "center";
            this.c.fillText(indicatorTxt, this.x + ringDist-10, this.y-3);
            this.c.closePath();
        }

        //Draw all the individual shots
        let shotsLength = shots.length;
        let shot_x = 0;
        let shot_y = 0;
        let shot_num = '';
        let font_size = '';
        for (let i=0; i<shotsLength; i++){
            shot_num = shots[i][0];
            shot_x = shots[i][1]*this.ratio;
            shot_y = shots[i][2]*this.ratio;
            //Draw Circle
            this.c.beginPath();
            this.c.arc(this.x + (shot_x), this.y - (shot_y), this.shotRadius, 0, Math.PI * 2, false);
            this.c.fillStyle = shotFill;
            //Check if outlier
            if (shots[i][5] === true) {
                this.c.fillStyle = 'red';
            }
            this.c.fill();
            this.c.strokeStyle = shotStroke;
            this.c.lineWidth = this.dpr;
            this.c.stroke();
            this.c.closePath();
            //Draw text
            this.c.beginPath();
            let font_size = this.shotRadius - 1
            this.c.font = `${font_size}px Arial`;
            this.c.fillStyle= shotText;
            this.c.textAlign = "center";
            this.c.fillText(shot_num, this.x + (shot_x), this.y - (shot_y)+5);
            this.c.closePath();
        }
        //Draw grouping circle if needed
        if (groupCircle) {
            for (let j=0; j<this.grouping.length; j++){
                console.log('drawing group')
                this.c.beginPath();
                this.c.arc(this.grouping[j].x, this.grouping[j].y, this.grouping[j].r, 0, Math.PI * 2, false);
                this.c.lineWidth = this.dpr;
                this.c.strokeStyle = groupColours[j];
                this.c.stroke();
                this.c.closePath();
            }
        }
    };

    this.init();
    this.draw();
    //The following variable is needed to changes/get values in the DrawTarget object within other functions e.g the ResizeSensor function
    let ThisTarget = this;

    //Set values for use in the later functions
    let canvasParent = this.canvasObj.parentNode;
    let canvasOffset = $("#" + canvasId).offset();
    //If the tooltip canvas object doesn't exist, create one
    let tipCanvas = document.getElementById('tip');
    if (!tipCanvas){
        tipCanvas = document.createElement("CANVAS");
        canvasParent.appendChild(tipCanvas);
        let tipWidth = 100*this.dpr;
        let tipHeight = 25*this.dpr;
        tipCanvas.setAttribute('width', `${tipWidth}`);
        tipCanvas.setAttribute('height', `${tipHeight}`);
        tipCanvas.setAttribute('id', 'tip');
        tipCanvas.style.width = '100px';
        tipCanvas.style.height = '25px';
        tipCanvas.style.zIndex = '10000';
        tipCanvas.style.left = "-20000px";
    }
    let tipCtx = tipCanvas.getContext('2d');

    //Change target dimensions if its parent div changes dimensions
    if (width === 'flex'){
        new ResizeSensor(canvasParent, function(){
            ThisTarget.update();
            ThisTarget.draw();
            canvasOffset = $("#" + canvasId).offset();
        });
    }
    canvasParent.addEventListener('mousemove', e => {
        handleMouseMove(e, shots, ThisTarget);
    });
    //Move the tooltip to the mouse when it hovers over a shot
    //used some code from https://stackoverflow.com/questions/17064913/display-tooltip-in-canvas-graph
    function handleMouseMove(e, shots, ThisTarget){
        //mousePageX and mousePageY are the positions of the mouse relative to the page (i.e (0,0) is the top left of the page)
        let mousePageX = (e.pageX - canvasOffset.left);
        let mousePageY = (e.pageY - canvasOffset.top);
        //mouseX and mouseY are the positions of the mouse relative to the center of the target (i.e (0,0) is the centre of the target)
        let mouseX = mousePageX*ThisTarget.dpr - ThisTarget.x;
        let mouseY = mousePageY*ThisTarget.dpr - ThisTarget.y;
        let hit = false;
        for (let i=0; i<shots.length; i++){
            //dx and dy are the difference between the position of a shot and the position of the mouse
            let dx =  mouseX - shots[i][1]*ThisTarget.ratio;
            let dy = mouseY + shots[i][2]*ThisTarget.ratio;
            //check if the mouse is within a certain distance of the shot position using the circle formula (x^2 + y^2 < r^2)
            if (dx*dx + dy*dy < ThisTarget.shotRadius*ThisTarget.shotRadius) {
                //Move the tooltip to near the mouse
                tipCanvas.style.left = (mousePageX + 25) + "px";
                tipCanvas.style.top = (mousePageY - 25) + "px";
                //fill the text in the tooltip
                tipCtx.clearRect(0, 0, tipCanvas.width, tipCanvas.height);
                tipCtx.font = 12*ThisTarget.dpr + 'px Arial';
                tipCtx.fillStyle = "white";
                tipCtx.fillText('Score: ' + shots[i][3], 5*ThisTarget.dpr, 15*ThisTarget.dpr);
                //set hit to true so that the x position of the tooltip doesn't get set to -200px
                hit = true;
            }


        }
        //if the mouse isn't on a shot, move the tooltip out of the screen
        if (!hit) { tipCanvas.style.left = "-20000px"; }
    }
}