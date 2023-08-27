// -------------------
//EXAMPLE DATA
// -------------------
// Normally you should fetch something simular from your server

// import http.client;

// conn = http.client.HTTPSConnection("imdb8.p.rapidapi.com")

// headers = {
//     'X-RapidAPI-Key': "64b7da5765msh05463c73329d118p13b331jsnb942a4d4fe82",
//     'X-RapidAPI-Host': "imdb8.p.rapidapi.com"
//     }

// conn.request("GET", "/auto-complete?q=game%20of%20thr", headers=headers)

// res = conn.getresponse()
// data = res.read()
// console.log('data')

// print(data.decode("utf-8"))

// const movie = {
//     image : "../../static/images/movie-x.jpg",
//     combinedPreference : 95,
//     balance : {
//       user1 : 75,
//       user2 : 81
//     },
//     movieCharacteristics : {
//       1 : {
//         name : "Animation",
//         image : "./",
//         user1 : 60,
//         user2 : 40
//       },
//       2 : {
//         name : "",
//         image : "./",
//         user1 : 60,
//         user2 : 40
//       },
//       3 : {
//         name : "Adventure",
//         image : "./",
//         user1 : 60,
//         user2 : 40
//       }
//     }
//   }
//   const data = [movie, movie, movie];
  
//   // --------------
//   // 
//   // --------------
//   $(document).ready(function(){
//     setMoviesColumn(data);
//   });
//   // --------------
//   // FUNCTIONS
//   // --------------
//   function setMoviesColumn(data) {
//     var movieImages = document.getElementsByClassName("movie-image")
//     console.log(movieImages);
//     let lenImages = 3;
//     for (let i = 0; i < lenImages; i++) {
//       console.log(movieImages[i].style)
//       console.log("url("+data[i].image+")")
//       movieImages[i].getElementsByClassName("image")[0].src = data[i].image;
//       // movieImages[i].style.backgroundImage = "url("+data[i].image+")";
//     }
//   }