function get_arr() {
    // var arr = JSON.stringify({'email':'tomb@raider.com','name':'LaraCroft'});
    // var data1 = new FormData()
    // data1.append('data1',arr)
    let xhr = new XMLHttpRequest();
    xhr.open('GET', 'upl_arr/');
    // xhr.setRequestHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    // xhr.responseType = "application/json";
    xhr.onload = function (e) {

        if (this.status == 200) {
            // var json = JSON.parse( JSON.parse(xhr.response)['dat'] );
            var json = JSON.parse(xhr.response)
            // console.log(json)
            genMain(json)

        } else {
        }
    }
    // xhr.onerror = function (ev){
    //     alert('Формирование заверщилось ошибкой')
    // }

    xhr.send();

}


function genMain(json) {
    $('.one').remove()
    $('.two').remove()

    for (var key in json) {
        let but = document.createElement('button');

        but.onclick = function () {
            genProduct(json[but.textContent][2], but.textContent, json)
        }
        but.textContent = key

        let inp = document.createElement('input');
        inp.className = 'size'
        inp.value = json[key][0]
        inp.setAttribute('data-path', [key])
        // console.log(inp.getAttribute('data-path'))
        inp.addEventListener('blur', function (e) {
            let targ = e.target
            json[targ.getAttribute('data-path')][0] = targ.value
            console.log(json)
        })

        let str_ = document.createElement('a')
        str_.textContent = '/' + json[key][1]

        let div_ = document.createElement('div');
        div_.className = 'one'
        div_.appendChild(but)
        div_.appendChild(inp)
        div_.appendChild(str_)

        $('#left').append(div_)

    }

    let div__ = document.createElement('div');
    div__.className = 'two'

    let per_ch = document.createElement('button');
    per_ch.textContent = 'Перерасчитать части'

    let sb_chast = document.createElement('button');
    sb_chast.textContent = 'Сбросить части'

    div__.appendChild(per_ch)
    div__.appendChild(sb_chast)

    $('#left').append(div__)

}

function genProduct(json, val_ch, global_json) {
    // console.log(json)
    $('.three').remove()

    for (var key in json) {

        let str_ = document.createElement('a')
        str_.textContent = key

        let div_ = document.createElement('div');
        div_.className = 'three'


        let inp = document.createElement('input');
        inp.className = 'size'
        inp.value = json[key][0]
        inp.setAttribute('data-path', [val_ch, key, 0])

        inp.addEventListener('blur', function (e) {
            let targ = e.target
            let arr = inp.getAttribute('data-path').split(',')
            // console.log(arr[0])
            // json[arr[1]][arr[2]] = targ.value
            global_json[arr[0]][2][arr[1]][arr[2]] = targ.value
            console.log(global_json)
        })


        let str__ = document.createElement('a')
        str__.textContent = '/' + json[key][1]


        div_.appendChild(str_)
        div_.appendChild(inp)
        div_.appendChild(str__)

        $('#right').append(div_)

        for (var key_ in json[key][2]) {


            let str__ = document.createElement('a')
            str__.textContent = key_

            let div__ = document.createElement('div');
            div__.className = 'three'

            //
            let inp__ = document.createElement('input');
            inp__.className = 'size'
            inp__.value = json[key][2][key_][0]
            inp__.setAttribute('data-path', [val_ch, key, key_, 0])

            inp__.addEventListener('blur', function (e) {
                let targ = e.target
                let arr = inp__.getAttribute('data-path').split(',')
                global_json[arr[0]][2][arr[1]][2][arr[2]][0] = targ.value
            })


            let str___ = document.createElement('a')
            if (typeof json[key][2][key_][1] == "undefined") {
                str___.textContent = ''
            } else {
                str___.textContent = '/' + json[key][2][key_][1]
            }


            div__.appendChild(str__)
            div__.appendChild(inp__)
            div__.appendChild(str___)


            $('#right').append(div__)
        }


        let div___ = document.createElement('div');
        div___.className = 'three'

        let per_pr = document.createElement('button');
        per_pr.textContent = 'Перерасчитать продукты'

        let sb_prod = document.createElement('button');
        sb_prod.textContent = 'Сбросить продукты'
        div___.appendChild(per_pr)
        div___.appendChild(sb_prod)
        $('#right').append(div___)


    }
}