/**
 * Mock Data Service for YouCam Skin Analysis
 * 
 * This service provides realistic mock data for development and testing
 * to avoid consuming API tokens during development.
 * 
 * Enable/disable via VITE_MOCK_MODE in .env file
 */

// Helper to generate random score within range
const randomScore = (min = 20, max = 95) => 
    Math.floor(Math.random() * (max - min + 1)) + min;

// Get level from score
const getLevelFromScore = (score) => {
    if (score >= 80) return { level: 'I', desc: 'Sangat Baik' };
    if (score >= 60) return { level: 'II', desc: 'Baik' };
    if (score >= 40) return { level: 'III', desc: 'Sedang' };
    if (score >= 20) return { level: 'IV', desc: 'Perlu Perhatian' };
    return { level: 'V', desc: 'Kritis' };
};

// Analysis text templates for each concern
const ANALYSIS_TEMPLATES = {
    oiliness: {
        I: {
            quantitative: 'Kulit Anda memiliki keseimbangan minyak yang sangat baik. Produksi sebum dalam kondisi optimal.',
            precautions: 'Pertahankan rutinitas perawatan saat ini. Gunakan pelembab ringan berbasis air.',
            recommendations: ['Pelembab gel ringan', 'Sunscreen non-comedogenic', 'Cleansing milk lembut']
        },
        II: {
            quantitative: 'Produksi sebum kulit Anda dalam kondisi baik dengan sedikit area berminyak di zona T.',
            precautions: 'Gunakan pembersih wajah yang gentle dua kali sehari.',
            recommendations: ['Oil-control moisturizer', 'Clay mask seminggu sekali', 'Toner dengan niacinamide']
        },
        III: {
            quantitative: 'Kulit campuran dengan sekresi sebum lebih banyak di zona T.',
            precautions: 'Perhatikan perlindungan terhadap sinar matahari dan atur kebiasaan makan.',
            recommendations: ['Pembersih berbusa lembut', 'Pelembab zone-specific', 'Blotting paper untuk zona T']
        },
        IV: {
            quantitative: 'Produksi sebum cukup tinggi terutama di area zona T.',
            precautions: 'Gunakan produk oil-free dan non-comedogenic.',
            recommendations: ['Gel cleanser dengan salicylic acid', 'Oil-free moisturizer', 'Mattifying primer']
        },
        V: {
            quantitative: 'Produksi sebum sangat berlebihan yang memerlukan penanganan intensif.',
            precautions: 'Konsultasikan dengan dermatolog untuk penanganan lebih lanjut.',
            recommendations: ['Konsultasi dermatolog', 'Retinoid topikal', 'Deep cleansing treatment']
        }
    },
    pore: {
        I: {
            quantitative: 'Pori-pori kulit Anda dalam kondisi sangat baik, hampir tidak terlihat.',
            precautions: 'Pertahankan rutinitas pembersihan yang baik.',
            recommendations: ['Gentle cleanser', 'Sunscreen SPF 30+', 'Antioxidant serum']
        },
        II: {
            quantitative: 'Pori-pori terlihat minimal dan dalam kondisi baik.',
            precautions: 'Lakukan pembersihan mendalam dan hidrasi dengan baik.',
            recommendations: ['Niacinamide serum', 'Clay mask mingguan', 'Toner astringent lembut']
        },
        III: {
            quantitative: 'Pori-pori yang tersumbat menyebabkan kulit menjadi gelap dan kusam.',
            precautions: 'Lakukan pembersihan mendalam dan gunakan produk penghapus penyumbatan pori-pori.',
            recommendations: ['AHA/BHA exfoliant', 'Pore-minimizing serum', 'Deep cleansing mask']
        },
        IV: {
            quantitative: 'Pori-pori terlihat cukup jelas terutama di area hidung dan pipi.',
            precautions: 'Hindari produk comedogenic dan lakukan eksfoliasi teratur.',
            recommendations: ['Retinol serum', 'Professional facial treatment', 'Salicylic acid cleanser']
        },
        V: {
            quantitative: 'Pori-pori sangat visible dan memerlukan perawatan intensif.',
            precautions: 'Segera konsultasi dengan dermatolog.',
            recommendations: ['Konsultasi dermatolog', 'Laser treatment', 'Medical-grade retinoid']
        }
    },
    age_spot: {
        I: {
            quantitative: 'Kulit Anda bebas dari flek dan bintik-bintik pigmentasi.',
            precautions: 'Terus gunakan sunscreen setiap hari.',
            recommendations: ['Sunscreen SPF 50', 'Vitamin C serum', 'Antioxidant moisturizer']
        },
        II: {
            quantitative: 'Ada beberapa area minor dengan pigmentasi ringan.',
            precautions: 'Tingkatkan penggunaan produk brightening.',
            recommendations: ['Brightening serum', 'Niacinamide', 'Physical sunscreen']
        },
        III: {
            quantitative: 'Kulit memiliki pigmentasi ringan akibat paparan sinar matahari.',
            precautions: 'Kendalikan mood, makan makanan sehat.',
            recommendations: ['Arbutin serum', 'Vitamin C treatment', 'Brightening mask']
        },
        IV: {
            quantitative: 'Terdapat beberapa area dengan flek dan bintik pigmentasi.',
            precautions: 'Gunakan produk depigmentasi secara konsisten.',
            recommendations: ['Chemical peel', 'Tranexamic acid serum', 'Azelaic acid']
        },
        V: {
            quantitative: 'Flek dan hiperpigmentasi cukup signifikan.',
            precautions: 'Konsultasi dengan dermatolog sangat dianjurkan.',
            recommendations: ['Konsultasi dermatolog', 'Laser treatment', 'Prescription depigmenting agents']
        }
    },
    wrinkle: {
        I: {
            quantitative: 'Kulit Anda hampir tidak memiliki kerutan dengan elastisitas sangat baik.',
            precautions: 'Pencegahan adalah kunci. Gunakan sunscreen dan antioksidan.',
            recommendations: ['Retinol 0.25%', 'Vitamin C serum', 'Peptide moisturizer']
        },
        II: {
            quantitative: 'Anda memiliki kerutan ringan yang masih dalam batas normal.',
            precautions: 'Perhatikan perlindungan terhadap sinar matahari.',
            recommendations: ['Retinol serum', 'Hyaluronic acid', 'Anti-aging moisturizer']
        },
        III: {
            quantitative: 'Serat kolagen sedikit hilang, elastisitas kulit berkurang.',
            precautions: 'Perhatikan perlindungan terhadap sinar matahari dan pelembab.',
            recommendations: ['Retinol 0.5%', 'Collagen-boosting serum', 'Eye cream dengan peptide']
        },
        IV: {
            quantitative: 'Kerutan visible di beberapa area wajah.',
            precautions: 'Pertimbangkan treatment profesional.',
            recommendations: ['Prescription retinoid', 'Professional treatment', 'Intensive anti-aging serum']
        },
        V: {
            quantitative: 'Kerutan dalam dan visible di berbagai area wajah.',
            precautions: 'Konsultasi dengan dermatolog sangat dianjurkan.',
            recommendations: ['Konsultasi aesthetic doctor', 'Injectable treatments', 'Laser resurfacing']
        }
    },
    acne: {
        I: {
            quantitative: 'Kulit Anda bebas dari jerawat aktif dalam kondisi sangat baik.',
            precautions: 'Pertahankan rutinitas pembersihan yang konsisten.',
            recommendations: ['Gentle cleanser', 'Non-comedogenic moisturizer', 'SPF ringan']
        },
        II: {
            quantitative: 'Ada beberapa bintik kecil atau komedo minor.',
            precautions: 'Gunakan produk dengan salicylic acid secara spot treatment.',
            recommendations: ['Salicylic acid cleanser', 'Spot treatment', 'Oil-free moisturizer']
        },
        III: {
            quantitative: 'Jerawat moderate dengan beberapa area peradangan.',
            precautions: 'Jaga suasana hati yang baik dan tidur yang cukup.',
            recommendations: ['Benzoyl peroxide', 'AHA/BHA exfoliant', 'Anti-bacterial treatment']
        },
        IV: {
            quantitative: 'Jerawat aktif cukup banyak dengan beberapa yang meradang.',
            precautions: 'Hindari makanan tinggi gula dan dairy.',
            recommendations: ['Prescription acne treatment', 'Adapalene gel', 'Professional facial']
        },
        V: {
            quantitative: 'Jerawat parah dengan peradangan signifikan.',
            precautions: 'Segera konsultasi dengan dermatolog.',
            recommendations: ['Konsultasi dermatolog segera', 'Oral medication', 'Professional acne treatment']
        }
    },
    dark_circle_v2: {
        I: {
            quantitative: 'Area bawah mata cerah dan bebas dari lingkaran hitam.',
            precautions: 'Pertahankan tidur yang cukup (7-8 jam).',
            recommendations: ['Eye cream dengan peptide', 'SPF eye cream', 'Silk pillowcase']
        },
        II: {
            quantitative: 'Ada sedikit bayangan di bawah mata yang masih dalam batas normal.',
            precautions: 'Tingkatkan kualitas tidur.',
            recommendations: ['Caffeine eye cream', 'Vitamin K serum', 'Cold compress']
        },
        III: {
            quantitative: 'Lingkaran hitam terlihat moderate.',
            precautions: 'Identifikasi penyebab spesifik (pigmentasi, vaskular, atau struktural).',
            recommendations: ['Vitamin C eye treatment', 'Retinol eye cream', 'Adequate sleep']
        },
        IV: {
            quantitative: 'Lingkaran hitam cukup prominent.',
            precautions: 'Pertimbangkan konsultasi dengan dermatolog.',
            recommendations: ['Professional eye treatment', 'Prescription lightening cream', 'Under-eye filler']
        },
        V: {
            quantitative: 'Lingkaran hitam sangat dark dan memerlukan evaluasi medis.',
            precautions: 'Konsultasi medis dianjurkan.',
            recommendations: ['Medical consultation', 'Laser treatment', 'PRP treatment']
        }
    },
    radiance: {
        I: {
            quantitative: 'Warna kulit sangat merata dan cerah dengan radiance natural.',
            precautions: 'Pertahankan dengan sunscreen dan antioksidan.',
            recommendations: ['Vitamin C serum', 'Brightening moisturizer', 'SPF 50']
        },
        II: {
            quantitative: 'Warna kulit cukup merata dengan sedikit variasi tone natural.',
            precautions: 'Gunakan produk brightening untuk mempertahankan keseragaman tone.',
            recommendations: ['AHA toner', 'Niacinamide serum', 'Even-tone moisturizer']
        },
        III: {
            quantitative: 'Ada beberapa area dengan tone yang tidak merata.',
            precautions: 'Fokus pada perlindungan UV dan produk brightening.',
            recommendations: ['Brightening serum', 'Alpha arbutin', 'High SPF sunscreen']
        },
        IV: {
            quantitative: 'Tone kulit tidak merata dengan beberapa area diskolorasi.',
            precautions: 'Pertimbangkan chemical peel atau treatment profesional.',
            recommendations: ['Professional brightening treatment', 'Tranexamic acid', 'Retinoid']
        },
        V: {
            quantitative: 'Diskolorasi signifikan yang memerlukan treatment komprehensif.',
            precautions: 'Konsultasi dermatolog untuk menentukan penyebab.',
            recommendations: ['Dermatologist consultation', 'Laser treatment', 'Chemical peel series']
        }
    },
    redness: {
        I: {
            quantitative: 'Kulit Anda sangat toleran tanpa tanda-tanda sensitivitas.',
            precautions: 'Pertahankan rutinitas yang gentle.',
            recommendations: ['Gentle cleanser', 'Barrier-supporting moisturizer', 'Minimal ingredient products']
        },
        II: {
            quantitative: 'Kulit memiliki sensitivitas minimal yang masih dalam batas normal.',
            precautions: 'Pilih produk yang fragrance-free.',
            recommendations: ['Fragrance-free products', 'Centella asiatica serum', 'Ceramide moisturizer']
        },
        III: {
            quantitative: 'Kulit menunjukkan sensitivitas moderate.',
            precautions: 'Hindari bahan iritan seperti alkohol dan fragrance.',
            recommendations: ['Soothing serum', 'Barrier repair cream', 'Gentle physical sunscreen']
        },
        IV: {
            quantitative: 'Kulit cukup sensitif dan mudah mengalami kemerahan.',
            precautions: 'Minimalkan jumlah produk yang digunakan.',
            recommendations: ['Ultra-gentle cleanser', 'Calming serum', 'Mineral sunscreen only']
        },
        V: {
            quantitative: 'Kulit sangat sensitif dan reaktif.',
            precautions: 'Konsultasi dengan dermatolog untuk diagnosis.',
            recommendations: ['Dermatologist consultation', 'Thermal water spray', 'Minimal skincare routine']
        }
    },
    firmness: {
        I: {
            quantitative: 'Serat kolagen kulit dalam kondisi sangat baik, kulit kencang dan elastis.',
            precautions: 'Pencegahan adalah yang terbaik. Lindungi kolagen dari kerusakan UV.',
            recommendations: ['Peptide serum', 'Vitamin C', 'Retinol preventive']
        },
        II: {
            quantitative: 'Struktur kolagen masih baik dengan sedikit penurunan natural.',
            precautions: 'Mulai gunakan produk collagen-boosting.',
            recommendations: ['Collagen-boosting serum', 'Hyaluronic acid', 'Antioxidants']
        },
        III: {
            quantitative: 'Serat kolagen sedikit hilang, elastisitas kulit berkurang.',
            precautions: 'Perhatikan perlindungan sinar matahari dan pelembab.',
            recommendations: ['Retinol therapy', 'Peptide complex', 'LED therapy']
        },
        IV: {
            quantitative: 'Penurunan kolagen signifikan menyebabkan loss of firmness.',
            precautions: 'Treatment profesional seperti radiofrequency dapat membantu.',
            recommendations: ['RF treatment', 'HIFU', 'Collagen supplements']
        },
        V: {
            quantitative: 'Degradasi kolagen signifikan. Kulit kehilangan elastisitas substantial.',
            precautions: 'Konsultasi dengan aesthetic doctor untuk treatment options.',
            recommendations: ['Aesthetic consultation', 'Thread lift', 'Injectable treatments']
        }
    }
};


// Generate analysis text for a concern based on score
const generateAnalysisText = (concern, score) => {
    const { level } = getLevelFromScore(score);
    const template = ANALYSIS_TEMPLATES[concern];
    
    if (!template || !template[level]) {
        // Fallback to pore template
        const fallback = ANALYSIS_TEMPLATES.pore[level];
        return {
            quantitative: fallback.quantitative,
            precautions: fallback.precautions,
            recommendations: fallback.recommendations
        };
    }
    
    return {
        quantitative: template[level].quantitative,
        precautions: template[level].precautions,
        recommendations: template[level].recommendations
    };
};

// 1x1 transparent PNG as placeholder
const PLACEHOLDER_IMAGE = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';

/**
 * Generate complete mock result data
 * @param {File} uploadedFile - The uploaded image file (used to create preview)
 * @returns {Promise<Object>} - Mock analysis result
 */
export async function generateMockResult(uploadedFile) {
    // Generate random scores for all concerns
    const scores = {
        all: { score: randomScore(50, 85) },
        skin_age: Math.floor(Math.random() * 20) + 20, // 20-40 years
        oiliness: { ui_score: randomScore(40, 90), whole: { ui_score: randomScore(40, 90) } },
        pore: { ui_score: randomScore(30, 85), whole: { ui_score: randomScore(30, 85) } },
        age_spot: { ui_score: randomScore(50, 95), whole: { ui_score: randomScore(50, 95) } },
        wrinkle: { ui_score: randomScore(45, 90), whole: { ui_score: randomScore(45, 90) } },
        acne: { ui_score: randomScore(55, 95), whole: { ui_score: randomScore(55, 95) } },
        dark_circle_v2: { ui_score: randomScore(40, 85), whole: { ui_score: randomScore(40, 85) } },
        radiance: { ui_score: randomScore(45, 88), whole: { ui_score: randomScore(45, 88) } },
        redness: { ui_score: randomScore(50, 90), whole: { ui_score: randomScore(50, 90) } },
        firmness: { ui_score: randomScore(40, 85), whole: { ui_score: randomScore(40, 85) } },
        texture: { ui_score: randomScore(45, 88), whole: { ui_score: randomScore(45, 88) } }
    };

    // Generate analysis texts based on scores
    const analysis_texts = {};
    const concernMappings = {
        oiliness: 'oiliness',
        pore: 'pore',
        age_spot: 'age_spot',
        wrinkle: 'wrinkle',
        acne: 'acne',
        dark_circle: 'dark_circle_v2',
        radiance: 'radiance',
        redness: 'redness',
        firmness: 'firmness'
    };

    for (const [textKey, scoreKey] of Object.entries(concernMappings)) {
        const scoreData = scores[scoreKey];
        const scoreValue = scoreData?.ui_score || scoreData?.whole?.ui_score || 50;
        analysis_texts[textKey] = generateAnalysisText(scoreKey, scoreValue);
    }

    // Convert uploaded file to base64 for original_image
    let original_image = PLACEHOLDER_IMAGE;
    if (uploadedFile) {
        try {
            original_image = await fileToBase64(uploadedFile);
        } catch (e) {
            console.warn('Could not convert uploaded file to base64:', e);
        }
    }

    // Use same image for composite (in real API, this would be analyzed/annotated)
    const composite_image = original_image;

    // Generate empty masks and overlays (placeholder)
    const masks = {};
    const concern_overlays = {};
    
    // In mock mode, we use the original image as overlays
    const concernKeys = ['acne', 'pore', 'wrinkle', 'age_spot', 'dark_circle', 'oiliness', 'radiance', 'redness', 'firmness'];
    for (const key of concernKeys) {
        concern_overlays[key] = original_image;
    }

    return {
        status: 'completed',
        task_id: `mock_${Date.now()}`,
        scores,
        original_image,
        composite_image,
        masks,
        concern_overlays,
        analysis_texts
    };
}

/**
 * Convert File to base64 string (without data URL prefix)
 */
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            // Remove "data:image/...;base64," prefix
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

/**
 * Simulate upload response (returns mock task_id)
 */
export function mockUploadResponse() {
    return {
        task_id: `mock_task_${Date.now()}`,
        status: 'processing'
    };
}

/**
 * Check if mock mode is enabled
 */
export function isMockMode() {
    return import.meta.env.VITE_MOCK_MODE === 'true';
}

/**
 * Get mock delay from env (default 2000ms)
 */
export function getMockDelay() {
    return parseInt(import.meta.env.VITE_MOCK_DELAY || '2000', 10);
}

/**
 * Simulate API delay
 */
export function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
