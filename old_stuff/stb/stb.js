		function myFunction() {
			var x = document.getElementById("headDiv");
			if (x.className === "headDiv") {
			x.className += " responsive";
			} else {
			x.className = "headDiv";
			}
		}

		window.onscroll = function() {
			if (window.pageYOffset > 120 && window.innerWidth > 700) {
				document.getElementById("headDiv").style.top = "-9vw";
				document.getElementById("headDiv").style.position = 'fixed'
				this.document.getElementById("googlePlay").style.top= '-0.4vw';
				this.document.getElementById("googlePlay").style.position= 'fixed';
			} 
			else if(window.pageYOffset <120) {
				document.getElementById("headDiv").style.top = "0vw";
				document.getElementById("headDiv").style.top = document.getElementById("headDiv").style.top
				document.getElementById("headDiv").style.position = 'absolute'
				document.getElementById("headDiv").style.opacity = 1
			}
		}

		// arrow animation
		var arrow_clicked = false;
		var arrow = document.getElementById("arrow") 

		arrow.onclick = function () {
	      this.classList.toggle ("checked");

	      if(arrow_clicked==false){
	      	window.scrollTo(0, document.body.scrollHeight || document.documentElement.scrollHeight)
	      	arrow_clicked = true;
	      }
	      else if(arrow_clicked==true){
	      	window.scrollTo(0, 0)
	      	arrow_clicked = false;
	      }
	    } 