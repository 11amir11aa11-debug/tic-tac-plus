let myId=null;
let player=null;


const cells=document.querySelectorAll(".cell");





async function login(){


let name=document.getElementById("name").value;


if(name.trim()=="") return;


let r=await fetch("/login",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

name:name

})

});


let data=await r.json();


myId=data.id;


document.getElementById("login").style.display="none";

document.getElementById("lobby").style.display="block";


document.getElementById("myName").innerHTML=
"👤 "+data.name;


}







async function playersList(){


if(!myId)return;


let r=await fetch("/players");


let list=await r.json();


let box=document.getElementById("players");


box.innerHTML="";



list.forEach(p=>{


if(p.id==myId)return;



let div=document.createElement("div");


div.className="player";


div.innerHTML=

p.name+

"<br><button onclick=\"invitePlayer('"+p.id+"')\">دعوت</button>";



box.appendChild(div);


});



}









async function invitePlayer(id){


await fetch("/invite",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

from:myId,

to:id

})

});


alert("دعوت ارسال شد");


}









async function checkInvite(){


if(!myId)return;


let r=await fetch("/check_invite",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

id:myId

})

});


let data=await r.json();



if(data.from){


document.getElementById("invite").innerHTML=

"🎮 دعوت بازی دریافت شد<br>"+

"<button onclick='acceptInvite()'>قبول</button>";


}


}







async function acceptInvite(){


await fetch("/accept",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

id:myId

})

});


checkGameStart();


}










async function checkGameStart(){


if(!myId || player)
return;



let r=await fetch("/join",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

id:myId

})

});



let data=await r.json();



if(data.player=="X" || data.player=="O"){


player=data.player;


document.getElementById("lobby").style.display="none";

document.getElementById("game").style.display="block";


document.getElementById("role").innerHTML=

"شما بازیکن "+player+" هستید";



updateGame(data.game);


}


}









async function getGame(){


if(!player)return;


let r=await fetch("/game");


let game=await r.json();


updateGame(game);


}








function updateGame(game){



game.board.forEach((x,i)=>{


if(x=="X"){


cells[i].innerHTML=

'<img src="assets/images/x.png">';


}


else if(x=="O"){


cells[i].innerHTML=

'<img src="assets/images/o.png">';


}


else{


cells[i].innerHTML="";


}



});




if(game.winner){

document.getElementById("status").innerHTML=

"🏆 برنده: "+game.winner;

}

else if(game.turn==player){

document.getElementById("status").innerHTML=

"🟢 نوبت شما";

}

else{

document.getElementById("status").innerHTML=

"⏳ نوبت حریف";

}


}









cells.forEach((cell,index)=>{


cell.onclick = async()=>{


if(!player) return;


try {


let r = await fetch("/move",{

method:"POST",

headers:{

"Content-Type":"application/json"

},

body:JSON.stringify({

id:myId,

index:index

})

});


let data = await r.json();



if(data.error){

document.getElementById("status").innerHTML =
"⚠️ " + data.error;

return;

}



updateGame(data);



}
catch(e){


document.getElementById("status").innerHTML =
"❌ خطا در اتصال به سرور";


}


};


});






setInterval(playersList,3000);

setInterval(checkInvite,3000);

setInterval(checkGameStart,3000);

setInterval(getGame,1000);
