"""Dynamic analysis text generation for skin concerns in Indonesian"""

from typing import TypedDict


class AnalysisText(TypedDict):
    """Structure for concern analysis text"""

    title: str
    level: str  # I, II, III, IV, V
    level_desc: str
    quantitative: str
    precautions: str
    recommendations: list[str]


def get_level_from_score(score: float) -> tuple[str, str]:
    """
    Convert 0-100 score to level I-V
    I = Excellent (80-100)
    II = Good (60-79)
    III = Moderate (40-59)
    IV = Needs Attention (20-39)
    V = Critical (0-19)
    """
    if score >= 80:
        return "I", "Sangat Baik"
    elif score >= 60:
        return "II", "Baik"
    elif score >= 40:
        return "III", "Sedang"
    elif score >= 20:
        return "IV", "Perlu Perhatian"
    else:
        return "V", "Kritis"


# ============================================
# LAPORAN PERMUKAAN (Surface Report) Texts
# ============================================

SEBUM_TEXTS = {
    "I": {
        "quantitative": "Kulit Anda memiliki keseimbangan minyak yang sangat baik. Produksi sebum dalam kondisi optimal, memberikan perlindungan alami tanpa menyebabkan kilap berlebih. Zona T dan zona U menunjukkan keseimbangan yang ideal.",
        "precautions": "Pertahankan rutinitas perawatan saat ini. Gunakan pelembab ringan berbasis air untuk menjaga keseimbangan. Hindari produk yang terlalu berat yang dapat mengganggu keseimbangan alami kulit.",
        "recommendations": [
            "Pelembab gel ringan",
            "Sunscreen non-comedogenic",
            "Cleansing milk lembut",
        ],
    },
    "II": {
        "quantitative": "Produksi sebum kulit Anda dalam kondisi baik. Terdapat sedikit area berminyak di zona T yang masih dalam batas normal. Kulit memiliki kelembaban natural yang cukup.",
        "precautions": "Gunakan pembersih wajah yang gentle dua kali sehari. Fokus pada zona T saat membersihkan. Hindari over-cleansing yang dapat memicu produksi minyak berlebih.",
        "recommendations": [
            "Oil-control moisturizer",
            "Clay mask seminggu sekali",
            "Toner dengan niacinamide",
        ],
    },
    "III": {
        "quantitative": "Kulit campuran adalah campuran kulit berminyak dan kulit kering. Ia memiliki ciri-ciri kulit berminyak dan kulit kering. Zona T memiliki sekresi sebum lebih banyak, dan zona U memiliki lebih sedikit sebum. Pelembab kulit harus dilakukan dengan baik untuk perawatan sehari-hari agar tidak terjadi produksi minyak berlebih. Gunakan produk pelembab pada pipi untuk perawatan dan perlindungan.",
        "precautions": "Perhatikan perlindungan terhadap sinar matahari, atur kebiasaan makan, kurangi asupan lemak, perbanyak makan makanan kaya vitamin seperti sayur dan buah, karena buah kaya vitamin C dan vitamin E yang efektif mencegah pigmentasi.",
        "recommendations": [
            "Pembersih berbusa lembut",
            "Pelembab zone-specific",
            "Blotting paper untuk zona T",
        ],
    },
    "IV": {
        "quantitative": "Produksi sebum cukup tinggi terutama di area zona T. Kulit cenderung terlihat berminyak dalam beberapa jam setelah dibersihkan. Pori-pori mungkin terlihat lebih besar akibat akumulasi sebum.",
        "precautions": "Bersihkan wajah secara teratur tetapi jangan berlebihan. Gunakan produk oil-free dan non-comedogenic. Pertimbangkan penggunaan produk dengan salicylic acid atau niacinamide.",
        "recommendations": [
            "Gel cleanser dengan salicylic acid",
            "Oil-free moisturizer",
            "Mattifying primer",
            "Chemical exfoliant BHA",
        ],
    },
    "V": {
        "quantitative": "Produksi sebum sangat berlebihan yang dapat menyebabkan masalah kulit seperti jerawat dan komedo. Kulit membutuhkan penanganan intensif untuk mengontrol minyak berlebih.",
        "precautions": "Konsultasikan dengan dermatolog untuk penanganan lebih lanjut. Hindari produk berbasis minyak. Jaga pola makan dengan mengurangi makanan berminyak dan bergula.",
        "recommendations": [
            "Konsultasi dermatolog",
            "Retinoid topikal",
            "Deep cleansing treatment",
            "Sebum-regulating serum",
        ],
    },
}

PORE_TEXTS = {
    "I": {
        "quantitative": "Pori-pori kulit Anda dalam kondisi sangat baik, hampir tidak terlihat. Tekstur kulit halus dan merata. Ini menunjukkan kesehatan kulit yang optimal.",
        "precautions": "Pertahankan rutinitas pembersihan yang baik. Gunakan sunscreen setiap hari untuk mencegah kerusakan kolagen yang dapat memperbesar pori.",
        "recommendations": ["Gentle cleanser", "Sunscreen SPF 30+", "Antioxidant serum"],
    },
    "II": {
        "quantitative": "Pori-pori terlihat minimal dan dalam kondisi baik. Ada beberapa area dengan pori sedikit lebih visible namun tidak signifikan.",
        "precautions": "Lakukan pembersihan mendalam dan hidrasi dengan baik setiap hari, dan hindari kerusakan pada pelindung kulit. Anda dapat memilih untuk menggunakan produk penghapus penyumbatan pori-pori dengan sisa minyak.",
        "recommendations": ["Niacinamide serum", "Clay mask mingguan", "Toner astringent lembut"],
    },
    "III": {
        "quantitative": "Pori-pori yang tersumbat menyebabkan kulit menjadi gelap dan kusam, permapasan kulit terhambat, dan mudah menyebabkan bakteri berkembang biak. Gemuk dan kotoran tidak bisa dikesampaikan, mudah menumpuk dan menyebabkan tersumbat kerak pada kulit. Untuk perawatan sehari-hari, perawatan mendalam dan pembersihan kerak pada kulit sangat efektif dalam mengecilkan pori-pori.",
        "precautions": "Lakukan pembersihan mendalam dan hidrasi dengan baik setiap hari, dan hindari kerusakan pada pelindung kulit. Anda dapat memilih untuk menggunakan produk penghapus penyumbatan pori-pori dengan sisa minyak. Masker pembersih mendalam dapat digunakan untuk membersihkan kulit, menghilangkan zat-zat yang tersumbat dan mengecilkan pori-pori.",
        "recommendations": ["AHA/BHA exfoliant", "Pore-minimizing serum", "Deep cleansing mask"],
    },
    "IV": {
        "quantitative": "Pori-pori terlihat cukup jelas terutama di area hidung dan pipi. Tekstur kulit tidak merata dan mudah menjadi tempat akumulasi kotoran dan sebum.",
        "precautions": "Hindari produk comedogenic. Lakukan eksfoliasi teratur tapi tidak berlebihan. Pertimbangkan treatment profesional seperti chemical peel atau microdermabrasion.",
        "recommendations": [
            "Retinol serum",
            "Professional facial treatment",
            "Pore-refining toner",
            "Salicylic acid cleanser",
        ],
    },
    "V": {
        "quantitative": "Pori-pori sangat visible dan melebar, menunjukkan kebutuhan akan perawatan intensif. Kondisi ini dapat menyebabkan masalah kulit lebih lanjut jika tidak ditangani.",
        "precautions": "Segera konsultasi dengan dermatolog. Hindari memegang atau memencet pori. Treatment profesional sangat direkomendasikan.",
        "recommendations": [
            "Konsultasi dermatolog",
            "Laser treatment",
            "Intensive pore treatment",
            "Medical-grade retinoid",
        ],
    },
}

FLEK_TEXTS = {
    "I": {
        "quantitative": "Kulit Anda bebas dari flek dan bintik-bintik pigmentasi. Warna kulit merata dan cerah. Ini menunjukkan perlindungan UV yang baik.",
        "precautions": "Terus gunakan sunscreen setiap hari bahkan saat cuaca mendung. Perlindungan UV adalah kunci untuk mempertahankan kulit bebas flek.",
        "recommendations": ["Sunscreen SPF 50", "Vitamin C serum", "Antioxidant moisturizer"],
    },
    "II": {
        "quantitative": "Ada beberapa area minor dengan pigmentasi ringan namun tidak signifikan. Kulit secara keseluruhan memiliki tone yang cukup merata.",
        "precautions": "Tingkatkan penggunaan produk brightening. Hindari paparan matahari langsung terutama jam 10-16.",
        "recommendations": ["Brightening serum", "Niacinamide", "Physical sunscreen"],
    },
    "III": {
        "quantitative": "Kulit memiliki pigmentasi ringan. Hiperpigmentasi adalah penggelapan kulit atau munculnya bintik-bintik, berair atau plak yang lebih gelap dari warna kulit normal karena faktor-faktor seperti paparan sinar matahari, genetika, dan metabolisme. Lakukan perlindungan dan hidrasi akan matahari yang ketat pada hari-hari yang tidak kental, hindari paparan sinar matahari yang terlalu lama dan radiasi yang kuat untuk memperparah sintesis melanin sehingga menghasilkan warna kulit lebih gelap. Gunakan produk yang mengandung arbutin, ekstrak kekedecatan hijau dan bahan lainnya untuk menekan sintesis dan menghambat sintesis melanin.",
        "precautions": "Kendalikan mood, makan makanan sehat, dan jangan menggunakan kosmetik inferior yang berbahaya bagi kulit, untuk mencegah kemungkinan timbulnya flek hitam. Suplemen vitamin C dan E dengan benar, dan makan lebih banyak buah dan sayuran segar.",
        "recommendations": [
            "Arbutin serum",
            "Vitamin C treatment",
            "Brightening mask",
            "SPF 50+ sunscreen",
        ],
    },
    "IV": {
        "quantitative": "Terdapat beberapa area dengan flek dan bintik pigmentasi yang visible. Kemungkinan disebabkan oleh paparan UV kumulatif atau faktor hormonal.",
        "precautions": "Gunakan produk depigmentasi secara konsisten. Pertimbangkan treatment profesional. Hindari produk yang dapat menyebabkan iritasi.",
        "recommendations": [
            "Hydroquinone (konsultasi dokter)",
            "Chemical peel",
            "Tranexamic acid serum",
            "Azelaic acid",
        ],
    },
    "V": {
        "quantitative": "Flek dan hiperpigmentasi cukup signifikan dan memerlukan penanganan profesional. Kondisi ini dapat disebabkan oleh berbagai faktor termasuk sun damage, melasma, atau post-inflammatory hyperpigmentation.",
        "precautions": "Konsultasi dengan dermatolog sangat dianjurkan. Hindari paparan matahari secara maksimal. Perawatan jangka panjang diperlukan.",
        "recommendations": [
            "Konsultasi dermatolog",
            "Laser treatment",
            "Prescription depigmenting agents",
            "Professional peel",
        ],
    },
}

WRINKLE_TEXTS = {
    "I": {
        "quantitative": "Kulit Anda hampir tidak memiliki kerutan. Elastisitas kulit sangat baik dengan garis halus minimal. Struktur kolagen dalam kondisi optimal.",
        "precautions": "Pencegahan adalah kunci. Gunakan sunscreen, antioksidan, dan retinol ringan untuk mempertahankan kondisi ini.",
        "recommendations": ["Retinol 0.25%", "Vitamin C serum", "Peptide moisturizer", "SPF 50"],
    },
    "II": {
        "quantitative": "Anda memiliki kerutan ringan. Kulit terpapar dalam jangka panjang dan dipengaruhi oleh lingkungan luar, radiasi UV menghasilkan radikal bebas oksigen aktif, menghancurkan kolagen jaringan, zat aktif, dan mengoksidasi sel-sel di membran sel, menyebabkan penyusutan kapiler setelah penuaan, kelembaban di pembuluh darah adalah berkurang dan nutrisi tidak mencukupi. Perawatan kulit sehari-hari yang tidak peduli pada tampilannya, mengakibatkan kerutan kecil yang pucat dan nyata, serta garis wajah menjadi lebih panjang dan dalam, serta semakin terlihat jelas saat Anda membuat ekspresi wajah.",
        "precautions": "Perhatikan perlindungan terhadap sinar matahari, kendalikan ekspresi wajah dan gerakan pagi, jaga status gizi yang baik, dan kurangi asupan garam.",
        "recommendations": [
            "Retinol serum",
            "Hyaluronic acid",
            "Facial massage",
            "Anti-aging moisturizer",
        ],
    },
    "III": {
        "quantitative": "Terdapat beberapa garis halus dan kerutan ringan, terutama di area ekspresi seperti sekitar mata dan dahi. Kolagen mulai berkurang secara natural seiring usia.",
        "precautions": "Intensifkan penggunaan produk anti-aging. Pertahankan hidrasi kulit yang optimal. Hindari gerakan wajah berulang yang berlebihan.",
        "recommendations": [
            "Retinol 0.5%",
            "Collagen-boosting serum",
            "Eye cream dengan peptide",
            "Weekly mask treatment",
        ],
    },
    "IV": {
        "quantitative": "Kerutan visible di beberapa area wajah. Elastisitas kulit menurun dan garis-garis lebih permanen mulai terbentuk.",
        "precautions": "Pertimbangkan treatment profesional seperti botox atau filler. Tingkatkan konsentrasi retinol secara bertahap. Konsultasi dengan dermatolog.",
        "recommendations": [
            "Prescription retinoid",
            "Professional treatment",
            "Intensive anti-aging serum",
            "Collagen supplements",
        ],
    },
    "V": {
        "quantitative": "Kerutan dalam dan visible di berbagai area wajah. Kerusakan kolagen signifikan yang memerlukan intervensi profesional.",
        "precautions": "Konsultasi dengan dermatolog atau aesthetic doctor sangat dianjurkan. Treatment medis mungkin diperlukan untuk hasil optimal.",
        "recommendations": [
            "Konsultasi aesthetic doctor",
            "Injectable treatments",
            "Laser resurfacing",
            "Medical-grade retinoid",
        ],
    },
}

ACNE_TEXTS = {
    "I": {
        "quantitative": "Kulit Anda bebas dari jerawat aktif. Kondisi kulit sangat baik tanpa tanda-tanda peradangan atau komedo.",
        "precautions": "Pertahankan rutinitas pembersihan yang konsisten. Hindari menyentuh wajah terlalu sering. Ganti sarung bantal secara teratur.",
        "recommendations": ["Gentle cleanser", "Non-comedogenic moisturizer", "SPF ringan"],
    },
    "II": {
        "quantitative": "Ada beberapa bintik kecil atau komedo minor. Kondisi ini sangat umum dan mudah dikontrol dengan perawatan rutin.",
        "precautions": "Gunakan produk dengan salicylic acid atau benzoyl peroxide secara spot treatment. Jangan memencet jerawat.",
        "recommendations": ["Salicylic acid cleanser", "Spot treatment", "Oil-free moisturizer"],
    },
    "III": {
        "quantitative": "Sejumlah besar neutrofil berkumpul di kelenjar pilosebaceous, dan folikel rambut tersumbat parah, membentuk lingkungan tertutup dan hipoksia, mengakibatkan perkembangbiakan bakteri anaerob dan Propionibacterium acnes, dan infeksi silang. Konsentrasi Propionibacterium juga meningkat sehingga menyebabkan jerawat dan peradangan sehingga membentuk jerawat di wajah.",
        "precautions": "Ketahuilah bahwa sinar UV matahari dapat memperparah jerawat. Jaga suasana hati yang baik, tidur yang cukup, hindari anarki yang memuncak, biasakan bangun pagi setiap hari untuk buang air besar, pertanyak olah raga, serta kerja dan istirahat yang normal. Dilarang menyentuh jerawat langsung dengan tangan untuk menghindari infeksi bakteri. Restoratif, detoksifikasi, dan produk hidrasi efisiensi tinggi dapat digunakan.",
        "recommendations": [
            "Benzoyl peroxide",
            "AHA/BHA exfoliant",
            "Anti-bacterial treatment",
            "Non-comedogenic sunscreen",
        ],
    },
    "IV": {
        "quantitative": "Jerawat aktif cukup banyak dengan beberapa yang meradang. Kondisi ini memerlukan perawatan lebih intensif dan konsisten.",
        "precautions": "Hindari makanan tinggi gula dan dairy. Jaga kebersihan alat makeup. Pertimbangkan konsultasi dengan dermatolog.",
        "recommendations": [
            "Prescription acne treatment",
            "Adapalene gel",
            "Antibacterial wash",
            "Professional facial",
        ],
    },
    "V": {
        "quantitative": "Jerawat parah dengan peradangan signifikan. Kondisi ini memerlukan penanganan medis profesional untuk mencegah scarring.",
        "precautions": "Segera konsultasi dengan dermatolog. Jangan mencoba memencet atau mengobati sendiri jerawat parah. Treatment medis diperlukan.",
        "recommendations": [
            "Konsultasi dermatolog segera",
            "Oral medication",
            "Professional acne treatment",
            "Isotretinoin (jika direkomendasikan)",
        ],
    },
}

KOMEDO_TEXTS = {
    "I": {
        "quantitative": "Kulit bebas dari komedo. Pori-pori bersih dan tidak tersumbat. Ini menunjukkan rutinitas pembersihan yang sangat baik.",
        "precautions": "Pertahankan pembersihan ganda (double cleansing) terutama jika menggunakan makeup atau sunscreen.",
        "recommendations": ["Oil cleanser", "Gentle foaming cleanser", "BHA toner"],
    },
    "II": {
        "quantitative": "Ada beberapa komedo minor di area hidung yang umum terjadi. Mudah dikontrol dengan perawatan rutin.",
        "precautions": "Gunakan produk dengan BHA secara teratur. Lakukan deep cleansing seminggu sekali.",
        "recommendations": ["Salicylic acid toner", "Pore strips (occasional)", "Clay mask"],
    },
    "III": {
        "quantitative": "Komedo visible di area T-zone. Disebabkan oleh akumulasi sebum dan sel kulit mati di dalam pori.",
        "precautions": "Eksfoliasi teratur dengan BHA. Hindari produk komedogenik. Jangan memencet komedo dengan tangan.",
        "recommendations": [
            "BHA exfoliant",
            "Retinol serum",
            "Deep pore cleanser",
            "Professional extraction",
        ],
    },
    "IV": {
        "quantitative": "Komedo cukup banyak di beberapa area wajah. Pori-pori membutuhkan pembersihan mendalam dan perawatan intensif.",
        "precautions": "Pertimbangkan professional facial extraction. Gunakan retinol untuk mencegah pembentukan komedo baru.",
        "recommendations": [
            "Prescription retinoid",
            "Professional facial",
            "Salicylic acid peel",
            "Niacinamide serum",
        ],
    },
    "V": {
        "quantitative": "Komedo sangat banyak dan dapat berkembang menjadi jerawat jika tidak ditangani. Memerlukan perawatan profesional.",
        "precautions": "Konsultasi dengan dermatolog dianjurkan. Treatment profesional seperti extraction atau chemical peel dapat membantu.",
        "recommendations": [
            "Dermatologist consultation",
            "Medical extraction",
            "Intensive pore treatment",
            "Prescription topicals",
        ],
    },
}

DARK_CIRCLE_TEXTS = {
    "I": {
        "quantitative": "Area bawah mata cerah dan bebas dari lingkaran hitam. Sirkulasi darah di area mata sangat baik.",
        "precautions": "Pertahankan tidur yang cukup (7-8 jam). Lindungi area mata dari paparan UV dengan sunscreen atau kacamata.",
        "recommendations": ["Eye cream dengan peptide", "SPF eye cream", "Silk pillowcase"],
    },
    "II": {
        "quantitative": "Ada sedikit bayangan di bawah mata yang masih dalam batas normal. Bisa disebabkan oleh kurang tidur sementara atau faktor genetik ringan.",
        "precautions": "Tingkatkan kualitas tidur. Gunakan eye cream dengan vitamin K atau caffeine.",
        "recommendations": ["Caffeine eye cream", "Vitamin K serum", "Cold compress"],
    },
    "III": {
        "quantitative": "Lingkaran hitam terlihat moderate. Dapat disebabkan oleh berbagai faktor termasuk kurang tidur, genetik, hiperpigmentasi, atau pembuluh darah yang terlihat.",
        "precautions": "Identifikasi penyebab spesifik (pigmentasi, vaskular, atau struktural). Sesuaikan treatment berdasarkan penyebab.",
        "recommendations": [
            "Vitamin C eye treatment",
            "Retinol eye cream",
            "Color-correcting concealer",
            "Adequate sleep",
        ],
    },
    "IV": {
        "quantitative": "Lingkaran hitam cukup prominent dan mempengaruhi tampilan keseluruhan. Perawatan intensif diperlukan.",
        "precautions": "Pertimbangkan konsultasi dengan dermatolog untuk treatment seperti chemical peel atau laser. Pastikan tidak ada underlying health condition.",
        "recommendations": [
            "Professional eye treatment",
            "Prescription lightening cream",
            "Under-eye filler (konsultasi)",
            "Iron supplements (jika diperlukan)",
        ],
    },
    "V": {
        "quantitative": "Lingkaran hitam sangat dark dan memerlukan evaluasi untuk menentukan penyebab serta treatment terbaik.",
        "precautions": "Konsultasi medis dianjurkan untuk menyingkirkan kondisi kesehatan underlying. Treatment profesional diperlukan.",
        "recommendations": [
            "Medical consultation",
            "Laser treatment",
            "PRP treatment",
            "Filler treatment",
        ],
    },
}

SKIN_TONE_TEXTS = {
    "I": {
        "quantitative": "Warna kulit sangat merata dan cerah. Kulit memiliki radiance natural yang sehat tanpa diskolorasi.",
        "precautions": "Pertahankan dengan sunscreen dan antioksidan. Hindari paparan UV berlebih yang dapat merusak tone kulit.",
        "recommendations": ["Vitamin C serum", "Brightening moisturizer", "SPF 50"],
    },
    "II": {
        "quantitative": "Warna kulit cukup merata dengan sedikit variasi tone yang natural. Kulit terlihat sehat.",
        "precautions": "Gunakan produk brightening untuk mempertahankan keseragaman tone. Eksfoliasi ringan membantu cell turnover.",
        "recommendations": ["AHA toner", "Niacinamide serum", "Even-tone moisturizer"],
    },
    "III": {
        "quantitative": "Ada beberapa area dengan tone yang tidak merata. Bisa disebabkan oleh sun damage, post-inflammatory hyperpigmentation, atau faktor lainnya.",
        "precautions": "Fokus pada perlindungan UV dan produk brightening. Eksfoliasi teratur membantu meratakan tone.",
        "recommendations": [
            "Brightening serum",
            "Alpha arbutin",
            "Regular exfoliation",
            "High SPF sunscreen",
        ],
    },
    "IV": {
        "quantitative": "Tone kulit tidak merata dengan beberapa area diskolorasi visible. Memerlukan treatment lebih intensif.",
        "precautions": "Pertimbangkan chemical peel atau treatment profesional. Konsistensi dalam penggunaan brightening agents penting.",
        "recommendations": [
            "Professional brightening treatment",
            "Tranexamic acid",
            "Kojic acid serum",
            "Retinoid",
        ],
    },
    "V": {
        "quantitative": "Diskolorasi signifikan yang memerlukan pendekatan treatment komprehensif.",
        "precautions": "Konsultasi dermatolog untuk menentukan penyebab dan treatment plan. Treatment kombinasi mungkin diperlukan.",
        "recommendations": [
            "Dermatologist consultation",
            "Prescription depigmenting agents",
            "Laser treatment",
            "Chemical peel series",
        ],
    },
}

# ============================================
# LAPORAN MENDALAM (Deep Report) Texts
# ============================================

SENSITIVITY_TEXTS = {
    "I": {
        "quantitative": "Kulit Anda sangat toleran dan tidak menunjukkan tanda-tanda sensitivitas. Barrier kulit dalam kondisi optimal.",
        "precautions": "Pertahankan rutinitas yang gentle. Hindari pergantian produk terlalu sering yang dapat mengganggu barrier.",
        "recommendations": [
            "Gentle cleanser",
            "Barrier-supporting moisturizer",
            "Minimal ingredient products",
        ],
    },
    "II": {
        "quantitative": "Kulit memiliki sensitivitas minimal yang masih dalam batas normal. Bereaksi baik terhadap sebagian besar produk.",
        "precautions": "Pilih produk yang fragrance-free. Lakukan patch test untuk produk baru.",
        "recommendations": [
            "Fragrance-free products",
            "Centella asiatica serum",
            "Ceramide moisturizer",
        ],
    },
    "III": {
        "quantitative": "Kulit menunjukkan sensitivitas moderate. Mungkin bereaksi terhadap beberapa bahan aktif atau perubahan lingkungan.",
        "precautions": "Hindari bahan iritan seperti alkohol dan fragrance. Perkenalkan produk baru secara perlahan. Fokus pada memperkuat skin barrier.",
        "recommendations": [
            "Soothing serum",
            "Barrier repair cream",
            "Gentle physical sunscreen",
            "Oat-based products",
        ],
    },
    "IV": {
        "quantitative": "Kulit cukup sensitif dan mudah mengalami kemerahan atau iritasi. Memerlukan perawatan khusus.",
        "precautions": "Minimalkan jumlah produk yang digunakan. Pilih produk untuk sensitive skin. Hindari eksfoliasi berlebihan.",
        "recommendations": [
            "Ultra-gentle cleanser",
            "Calming serum",
            "Hypoallergenic moisturizer",
            "Mineral sunscreen only",
        ],
    },
    "V": {
        "quantitative": "Kulit sangat sensitif dan reaktif. Mungkin menunjukkan tanda-tanda rosacea atau kondisi kulit lainnya.",
        "precautions": "Konsultasi dengan dermatolog untuk diagnosis dan treatment. Gunakan produk seminimal mungkin.",
        "recommendations": [
            "Dermatologist consultation",
            "Prescription-only products",
            "Thermal water spray",
            "Minimal skincare routine",
        ],
    },
}

UV_SPOT_TEXTS = {
    "I": {
        "quantitative": "Tidak terdeteksi kerusakan UV pada kulit. Perlindungan matahari Anda sangat efektif.",
        "precautions": "Teruskan kebiasaan sun protection yang baik. Reapply sunscreen setiap 2 jam saat di luar ruangan.",
        "recommendations": ["Broad-spectrum SPF 50", "Antioxidant serum", "UV-protective clothing"],
    },
    "II": {
        "quantitative": "Kerusakan UV minimal. Ada beberapa tanda exposure yang tidak signifikan.",
        "precautions": "Tingkatkan frekuensi sunscreen application. Gunakan topi dan kacamata untuk perlindungan tambahan.",
        "recommendations": ["High SPF sunscreen", "Vitamin C", "DNA repair enzyme products"],
    },
    "III": {
        "quantitative": "Kerusakan UV moderate terdeteksi. Kulit menunjukkan tanda-tanda paparan matahari kumulatif.",
        "precautions": "Perlindungan UV maksimal diperlukan. Gunakan produk repair dan antioksidan.",
        "recommendations": [
            "SPF 50+ daily",
            "Retinol at night",
            "Niacinamide",
            "Professional consultation",
        ],
    },
    "IV": {
        "quantitative": "Kerusakan UV cukup signifikan. Perlu perawatan untuk memperbaiki dan mencegah kerusakan lebih lanjut.",
        "precautions": "Hindari paparan matahari langsung sebisa mungkin. Treatment profesional mungkin diperlukan.",
        "recommendations": [
            "Strict sun avoidance",
            "Prescription retinoid",
            "Chemical peel",
            "Laser treatment",
        ],
    },
    "V": {
        "quantitative": "Kerusakan UV signifikan yang memerlukan evaluasi medis untuk menyingkirkan kondisi pre-cancerous.",
        "precautions": "Konsultasi dermatolog segera. Screening rutin untuk skin cancer dianjurkan.",
        "recommendations": [
            "Immediate dermatologist visit",
            "Skin cancer screening",
            "Medical-grade treatment",
            "Maximum sun protection",
        ],
    },
}

PIGMENT_TEXTS = {
    "I": {
        "quantitative": "Distribusi melanin sangat merata. Tidak ada hiperpigmentasi yang terdeteksi.",
        "precautions": "Pertahankan dengan sun protection dan antioksidan untuk mencegah pembentukan pigmentasi baru.",
        "recommendations": ["Vitamin C serum", "Niacinamide", "Broad-spectrum sunscreen"],
    },
    "II": {
        "quantitative": "Pigmentasi minimal dan merata. Kulit memiliki tone yang seimbang.",
        "precautions": "Gunakan brightening agents untuk mempertahankan tone. Lindungi dari UV.",
        "recommendations": ["Alpha arbutin", "Kojic acid", "Regular sunscreen use"],
    },
    "III": {
        "quantitative": "Ada beberapa area dengan akumulasi pigmen yang lebih tinggi. Bisa berupa melasma, sun spots, atau PIH.",
        "precautions": "Identifikasi jenis pigmentasi untuk treatment yang tepat. Konsistensi adalah kunci.",
        "recommendations": [
            "Tranexamic acid",
            "Hydroquinone (short-term)",
            "Azelaic acid",
            "Chemical peel",
        ],
    },
    "IV": {
        "quantitative": "Pigmentasi tidak merata yang cukup visible. Memerlukan treatment kombinasi untuk hasil optimal.",
        "precautions": "Pertimbangkan treatment profesional. Sabarlah karena treatment pigmentasi membutuhkan waktu.",
        "recommendations": [
            "Professional peels",
            "Laser treatment",
            "Prescription depigmenting",
            "Combination therapy",
        ],
    },
    "V": {
        "quantitative": "Hiperpigmentasi signifikan yang memerlukan pendekatan komprehensif dan mungkin treatment medis.",
        "precautions": "Konsultasi dengan dermatolog untuk diagnosis dan treatment plan yang tepat.",
        "recommendations": [
            "Dermatologist consultation",
            "Combination laser therapy",
            "Oral tranexamic acid",
            "Long-term treatment plan",
        ],
    },
}

COLLAGEN_TEXTS = {
    "I": {
        "quantitative": "Serat kolagen kulit dalam kondisi sangat baik. Kulit kencang dan elastis dengan struktur yang optimal.",
        "precautions": "Pencegahan adalah yang terbaik. Lindungi kolagen dari kerusakan UV dan polusi.",
        "recommendations": ["Peptide serum", "Vitamin C", "Retinol preventive", "Daily SPF"],
    },
    "II": {
        "quantitative": "Struktur kolagen masih baik dengan sedikit penurunan natural sesuai usia.",
        "precautions": "Mulai gunakan produk collagen-boosting. Hidrasi yang cukup membantu mempertahankan elastisitas.",
        "recommendations": [
            "Collagen-boosting serum",
            "Hyaluronic acid",
            "Facial massage",
            "Antioxidants",
        ],
    },
    "III": {
        "quantitative": "Serat kolagen sedikit hilang, dan struktur jaringan tekstur yang dibentuk oleh serat kolagen dan serat elastis di dermis secara bertahap hancur, dan kulit mengempis. Elastisitas kulit yang tidak memadai menyebabkan garis-garis halus semakin dalam dan munculnya keriput. Perlindungan terhadap sinar matahari harus diperkuat dalam perawatan sehari-hari, dan produk perawatan kulit yang mengandung vitamin C, E, ekstrak teh hijau, ekstrak kulit putih dan bahan lainnya juga dapat digunakan untuk mencegah efek anti-oksidasi dan meningkatkat radikal bebas.",
        "precautions": "Perhatikan perlindungan terhadap sinar matahari, hindari sinar UV langsung, dan perhatikan pelembab. Makan lebih sehat makanan olahan, makanan kembung dan minuman berkarbonasi, dan makan makanan yang kaya kolagen dan vitamin C. Untuk menjaga nidras hidup yang baik, Anda dapat mengonsumsi produk yang mengandung peptide, alkohol teh putih dan bahan lainnya untuk meningkatkan sintesis kolagen dan meningkatkan elastisitas kulit.",
        "recommendations": ["Retinol therapy", "Peptide complex", "Microneedling", "LED therapy"],
    },
    "IV": {
        "quantitative": "Penurunan kolagen signifikan yang menyebabkan loss of firmness dan elastisitas.",
        "precautions": "Treatment profesional seperti radiofrequency atau ultrasound lifting dapat membantu. Konsultasi dengan aesthetic doctor.",
        "recommendations": [
            "RF treatment",
            "HIFU",
            "Professional-grade retinoid",
            "Collagen supplements",
        ],
    },
    "V": {
        "quantitative": "Degradasi kolagen signifikan. Kulit kehilangan elastisitas dan firmness secara substantial.",
        "precautions": "Konsultasi dengan aesthetic doctor untuk treatment options. Kombinasi treatment mungkin diperlukan.",
        "recommendations": [
            "Aesthetic consultation",
            "Thread lift",
            "Injectable treatments",
            "Intensive professional care",
        ],
    },
}


# ============================================
# Main Function to Get Analysis Text
# ============================================

CONCERN_TEXTS = {
    # Laporan Permukaan
    "sebum": SEBUM_TEXTS,
    "oiliness": SEBUM_TEXTS,
    "pore": PORE_TEXTS,
    "flek": FLEK_TEXTS,
    "age_spot": FLEK_TEXTS,
    "wrinkle": WRINKLE_TEXTS,
    "acne": ACNE_TEXTS,
    "komedo": KOMEDO_TEXTS,
    "dark_circle": DARK_CIRCLE_TEXTS,
    "dark_circle_v2": DARK_CIRCLE_TEXTS,
    "skin_tone": SKIN_TONE_TEXTS,
    "radiance": SKIN_TONE_TEXTS,
    "texture": SKIN_TONE_TEXTS,
    # Laporan Mendalam
    "sensitivity": SENSITIVITY_TEXTS,
    "redness": SENSITIVITY_TEXTS,
    "uv_spot": UV_SPOT_TEXTS,
    "pigment": PIGMENT_TEXTS,
    "collagen": COLLAGEN_TEXTS,
    "firmness": COLLAGEN_TEXTS,
}


def get_analysis_text(concern: str, score: float) -> AnalysisText:
    """
    Get analysis text for a specific concern based on score

    Args:
        concern: The concern type (e.g., 'acne', 'pore', 'wrinkle')
        score: The score value (0-100)

    Returns:
        AnalysisText dict with all text components
    """
    level, level_desc = get_level_from_score(score)

    # Get texts for this concern, default to generic if not found
    concern_lower = concern.lower().replace("-", "_")
    texts = CONCERN_TEXTS.get(concern_lower, PORE_TEXTS)  # Default to pore if not found

    level_texts = texts.get(level, texts.get("III"))  # Default to level III if not found

    return {
        "title": concern.replace("_", " ").title(),
        "level": level,
        "level_desc": level_desc,
        "quantitative": level_texts["quantitative"],
        "precautions": level_texts["precautions"],
        "recommendations": level_texts["recommendations"],
    }


def generate_all_analysis_texts(scores: dict) -> dict[str, AnalysisText]:
    """
    Generate analysis texts for all available scores

    Args:
        scores: The scores dict from YouCam API

    Returns:
        Dict mapping concern names to their analysis texts
    """
    result = {}

    # Map of YouCam score keys to our concern names
    score_mappings = {
        "oiliness": "sebum",
        "pore": "pore",
        "age_spot": "flek",
        "wrinkle": "wrinkle",
        "acne": "acne",
        "dark_circle_v2": "dark_circle",
        "radiance": "skin_tone",
        "texture": "texture",
        "redness": "sensitivity",
        "firmness": "collagen",
    }

    for youcam_key, concern_name in score_mappings.items():
        score_data = scores.get(youcam_key)
        if score_data:
            # Extract score value (handle different score structures)
            if isinstance(score_data, dict):
                if "ui_score" in score_data:
                    score_val = score_data["ui_score"]
                elif "whole" in score_data and "ui_score" in score_data["whole"]:
                    score_val = score_data["whole"]["ui_score"]
                elif "score" in score_data:
                    score_val = score_data["score"]
                else:
                    continue
            else:
                score_val = float(score_data)

            result[concern_name] = get_analysis_text(concern_name, score_val)

    return result
