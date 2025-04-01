function startSequence() {
    const dot = document.getElementById("targetDot");
    const startText = document.getElementById("startText");
    startText.style.display = "none";

    const positions = [
        { top: 20, left: 20 },                         // top-left
        { top: 20, right: 20 },                        // top-right
        { bottom: 20, left: 20 },                      // bottom-left
        { bottom: 20, right: 20 },                     // bottom-right
        { top: "50%", left: "50%", center: true }      // center
    ];

    let i = 0;

    const moveDot = () => {
        if (i >= positions.length) {
            dot.style.display = "none";
            setTimeout(() => {
                startText.style.display = "block";
            }, 500); // slight delay before showing text again
            return;
        }

        const pos = positions[i];
        dot.style.display = "block";
        dot.style.top = "";
        dot.style.left = "";
        dot.style.right = "";
        dot.style.bottom = "";
        dot.style.transform = "";

        if (pos.center) {
            dot.style.top = pos.top;
            dot.style.left = pos.left;
            dot.style.transform = "translate(-50%, -50%)";
        } else {
            for (let key in pos) {
                dot.style[key] = typeof pos[key] === "number" ? pos[key] + "px" : pos[key];
            }
        }

        i++;
        setTimeout(() => {
            dot.style.display = "none";
            setTimeout(moveDot, 500); // pause before next dot
        }, 5000); // show dot for 5 seconds
    };

    moveDot();
}
