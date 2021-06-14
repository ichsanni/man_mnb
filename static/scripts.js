async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
async function goFetch(){
    let processUpdate = true;

    do {
        await sleep(3000);
        fetch("/status",{
            method: 'GET',
            headers: {'Content-Type': 'application/json'},
            })
        .then(response => response.json())
        .then(function(json){
            let laporan = document.getElementById('laporan');
            laporan.innerHTML = "STATUS MODEL: " + ((json['overall'] === '2') ? '✅ Selesai melatih model':
                                                    (json['overall'] === '1') ? 'Sedang melatih model' : '❌ Belum mulai melatih model') + "<br><br>" +
                                "STATUS PREPROCESSING MODEL:" + "<br>" +
                                ((json['casefolding'] === '1') ? '✅':'❌') + "    Case-folding " +  "<br>" +
                                ((json['filtering'] === '1') ? '✅':'❌') + "    Filtering " + "<br>" +
                                ((json['stemming'] === json['totalstemmed']) ? '✅':'❌') + "    Teks yang telah di-stem: " + json['stemming'] + " dari " + json['totalstemmed'] + " teks<br>" +
                                ((json['tokenizing'] === '1') ? '✅':'❌') + "    Tokenizing " +  "<br><br>" + 
                                "STATISTIK:" + "<br>" +
                                ((json['accuracy'] !== '0') ? '✅':'❌') + "    Akurasi model: " + json['accuracy'] + "<br>" +
                                ((json['negatif'] !== '0') ? '✅':'❌') + "    Jumlah teks bersentimen negatif: " + json['negatif'] + "<br>" + 
                                ((json['positif'] !== '0') ? '✅':'❌') + "    Jumlah teks bersentimen positif: " + json['positif'] + "<br>" +
                                "K-FOLD CROSS VALIDATION:" + "<br>" +
                                ((json['kfold'] !== '0') ? '✅':'❌') + "    Akurasi K-Fold Cross Validation: " + json['kfold'] + "<br>" + 
                                ((json['avg_kfold'] !== '0') ? '✅':'❌') + "    Rata-rata akurasi K-Fold: " + json['avg_kfold'];    
            if (json['overall'] !== '1' && json['overall'] !== 'undefined'){
                processUpdate = false;
                document.getElementById('unggah').disabled = false;
                } 
        });            
    }
    while(processUpdate);
    if(!processUpdate){

        let imgHist = document.createElement('img');
        imgHist.setAttribute('src', 'static/histogram.png');

        let imgKFold = document.createElement('img');
        imgKFold.setAttribute('src', 'static/kfold.png');

        let imgConf = document.createElement('img');
        imgConf.setAttribute('src', 'static/conf_matrix.png');

        document.querySelector('#hist').innerHTML = '';
        document.querySelector('#hist').append(imgHist);
        document.querySelector('#kfold').innerHTML = '';
        document.querySelector('#kfold').append(imgKFold);
        document.querySelector('#conf').innerHTML = '';
        document.querySelector('#conf').append(imgConf);
    }
}

function uploadFile(e){
    let file = e.target.files;
    let formData = new FormData();
    formData.append('file', file[0]);

    fetch('/unggah', {
            method: 'POST',
            body: formData
        })
    .then(response => response.json())
    .then(function(json){
        console.log('uploaded file');
        if(json['status'] === '200'){
            fetch("/latih",{
                method: 'GET'
                })
            .then(response => response.json())
            .then(function(json){
                console.log('training model');
                console.log(json);
            });
        }
    });
    goFetch();
}

document.querySelector('#unggah').addEventListener('change', event => {
    uploadFile(event);
    document.getElementById('unggah').disabled = true;
});

document.querySelector('#delAll').addEventListener('click', event => {
    if(confirm("Apakah anda yakin ingin menghapus semua data dan model yang telah dilatih?")){
        fetch("/delete",{
            method: 'GET',
            })
        .then(response => response.json())
        .then(function(json){
            if(json['status'] == '200'){
                alert('Data telah dihapus.');
                location.reload(true); 
            }
        })
    }
})