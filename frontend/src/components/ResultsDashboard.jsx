import React, { useState } from 'react';
import { Activity, ChevronRight } from 'lucide-react';
import SemiCircularGauge from './SemiCircularGauge';
import ImageComparisonSlider from './ImageComparisonSlider';
import ConcernDetail from './ConcernDetail';
import './ResultsDashboard.css';

// Tab and concern configuration
const MAIN_TABS = [
    { id: 'umum', label: 'Laporan Umum' },
    { id: 'permukaan', label: 'Laporan Permukaan' },
    { id: 'mendalam', label: 'Laporan Mendalam' },
];

const PERMUKAAN_CONCERNS = [
    { id: 'sebum', label: 'Sebum', key: 'oiliness' },
    { id: 'pori', label: 'Pori-Pori', key: 'pore' },
    { id: 'flek', label: 'Flek', key: 'age_spot' },
    { id: 'keriput', label: 'Keriput', key: 'wrinkle' },
    { id: 'jerawat', label: 'Jerawat', key: 'acne' },
    { id: 'komedo', label: 'Komedo', key: 'pore' }, // Maps to pore
    { id: 'warna', label: 'Warna Kulit', key: 'radiance' },
    { id: 'lingkaran', label: 'Lingkaran Hitam', key: 'dark_circle_v2' },
];

const MENDALAM_CONCERNS = [
    { id: 'sensitivitas', label: 'Sensitivitas PL', key: 'redness' },
    { id: 'titik_uv', label: 'Titik UV', key: 'age_spot' },
    { id: 'pigmen', label: 'Pigmen', key: 'age_spot' }, // Combined visualization
    { id: 'jerawat_uv', label: 'Jerawat UV', key: 'acne' },
    { id: 'kolagen', label: 'Serat Kolagen', key: 'firmness' },
];

export default function ResultsDashboard({ results }) {
    const [activeMainTab, setActiveMainTab] = useState('umum');
    const [activeSubTab, setActiveSubTab] = useState(null);

    if (!results || !results.scores) {
        return null;
    }

    const { scores, composite_image, masks, original_image, analysis_texts, concern_overlays } = results;

    // Extract score value from various score structures
    const getScoreValue = (key) => {
        const data = scores[key];
        if (!data) return null;

        if (typeof data === 'number') return data;
        if (data.ui_score !== undefined) return data.ui_score;
        if (data.whole?.ui_score !== undefined) return data.whole.ui_score;
        if (data.score !== undefined) return data.score;
        return null;
    };

    // Get mask image for a concern
    const getMaskImage = (key) => {
        if (!masks) return null;

        // Find matching mask file
        const matchingKey = Object.keys(masks).find(
            (name) => name.toLowerCase().includes(key.toLowerCase())
        );

        if (matchingKey && masks[matchingKey]) {
            return `data:image/png;base64,${masks[matchingKey]}`;
        }
        return null;
    };

    // Get concern overlay image (colored visualization)
    const getConcernOverlay = (key) => {
        if (!concern_overlays) return null;

        // Direct key match
        const cleanKey = key.replace('_v2', '');
        if (concern_overlays[cleanKey]) {
            return `data:image/jpeg;base64,${concern_overlays[cleanKey]}`;
        }

        // Try partial match
        const matchingKey = Object.keys(concern_overlays).find(
            (name) => name.toLowerCase().includes(cleanKey.toLowerCase())
        );

        if (matchingKey && concern_overlays[matchingKey]) {
            return `data:image/jpeg;base64,${concern_overlays[matchingKey]}`;
        }

        // Fallback to composite
        return composite_image ? `data:image/jpeg;base64,${composite_image}` : null;
    };

    // Calculate overall scores for summary
    const overallScore = Math.round(scores.all?.score || 0);
    const skinAge = scores.skin_age || 0;

    // Get top concerns (lowest scores) for summary
    const getTopConcerns = () => {
        const allConcerns = [...PERMUKAAN_CONCERNS, ...MENDALAM_CONCERNS];
        return allConcerns
            .map((concern) => ({
                ...concern,
                score: getScoreValue(concern.key),
            }))
            .filter((c) => c.score !== null)
            .sort((a, b) => a.score - b.score)
            .slice(0, 3);
    };

    const topConcerns = getTopConcerns();

    // Render Laporan Umum (General Report)
    const renderLaporanUmum = () => (
        <div className="laporan-umum">
            {/* Header Cards */}
            <div className="header-cards">
                <div className="header-card glass-card">
                    <h2 className="header-card-title">Skor Kulit Keseluruhan</h2>
                    <div className="header-card-value">{overallScore}</div>
                    <p className="header-card-subtitle">dari 100</p>
                </div>
                <div className="header-card glass-card">
                    <h2 className="header-card-title">Usia Kulit</h2>
                    <div className="header-card-value skin-age">{skinAge}</div>
                    <p className="header-card-subtitle">Tahun</p>
                </div>
            </div>

            {/* Main composite image with comparison slider */}
            {original_image && composite_image && (
                <div className="main-visual">
                    <ImageComparisonSlider
                        beforeImage={`data:image/jpeg;base64,${original_image}`}
                        afterImage={`data:image/jpeg;base64,${composite_image}`}
                        beforeLabel="Original"
                        afterLabel="Analisis"
                    />
                </div>
            )}

            {/* Surface Index Summary */}
            <div className="index-section glass-card">
                <h3 className="section-title">
                    <Activity size={18} />
                    Indeks Umum Kulit Permukaan
                </h3>
                <div className="index-bar-container">
                    <div
                        className="index-bar"
                        style={{
                            width: `${overallScore}%`,
                            background: `linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%)`,
                        }}
                    />
                    <div
                        className="index-indicator"
                        style={{ left: `${overallScore}%` }}
                    />
                </div>
                <div className="index-labels">
                    <span>Buruk</span>
                    <span>Sedang</span>
                    <span>Baik</span>
                </div>
            </div>

            {/* Deep Index Summary */}
            <div className="index-section glass-card">
                <h3 className="section-title">
                    <Activity size={18} />
                    Indeks Umum Kulit Mendalam
                </h3>
                <div className="index-bar-container">
                    <div
                        className="index-bar"
                        style={{
                            width: `${overallScore}%`,
                            background: `linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%)`,
                        }}
                    />
                    <div
                        className="index-indicator"
                        style={{ left: `${overallScore}%` }}
                    />
                </div>
                <div className="index-labels">
                    <span>Buruk</span>
                    <span>Sedang</span>
                    <span>Baik</span>
                </div>
            </div>

            {/* Top Concerns */}
            <div className="top-concerns glass-card">
                <h3 className="section-title">
                    <Activity size={18} />
                    Area Perhatian Utama
                </h3>
                <div className="concern-cards">
                    {topConcerns.map((concern, index) => (
                        <div
                            key={concern.id}
                            className="concern-mini-card"
                            onClick={() => {
                                const isPermukaan = PERMUKAAN_CONCERNS.some(
                                    (c) => c.id === concern.id
                                );
                                setActiveMainTab(isPermukaan ? 'permukaan' : 'mendalam');
                                setActiveSubTab(concern.id);
                            }}
                        >
                            <span className="concern-rank">#{index + 1}</span>
                            <span className="concern-name">{concern.label}</span>
                            <span
                                className={`concern-score ${
                                    concern.score >= 75
                                        ? 'excellent'
                                        : concern.score >= 50
                                        ? 'good'
                                        : 'attention'
                                }`}
                            >
                                {Math.round(concern.score)}
                            </span>
                            <ChevronRight size={16} />
                        </div>
                    ))}
                </div>
            </div>

            {/* Score Guide */}
            <div className="score-guide glass-card">
                <h3 className="guide-title">Panduan Skor</h3>
                <div className="guide-items">
                    <div className="guide-item">
                        <div className="guide-color excellent" />
                        <span>75-100: Sangat Baik</span>
                    </div>
                    <div className="guide-item">
                        <div className="guide-color good" />
                        <span>50-74: Baik</span>
                    </div>
                    <div className="guide-item">
                        <div className="guide-color attention" />
                        <span>0-49: Perlu Perhatian</span>
                    </div>
                </div>
            </div>
        </div>
    );

    // Render Laporan Permukaan or Mendalam with sub-tabs
    const renderLaporanDetail = () => {
        const concerns = activeMainTab === 'permukaan' ? PERMUKAAN_CONCERNS : MENDALAM_CONCERNS;
        const currentConcern = concerns.find((c) => c.id === activeSubTab) || concerns[0];

        return (
            <div className="laporan-detail">
                {/* Sub-tabs */}
                <div className="sub-tabs">
                    {concerns.map((concern) => (
                        <button
                            key={concern.id}
                            className={`sub-tab ${
                                (activeSubTab || concerns[0].id) === concern.id ? 'active' : ''
                            }`}
                            onClick={() => setActiveSubTab(concern.id)}
                        >
                            {concern.label}
                        </button>
                    ))}
                </div>

                {/* Concern Detail */}
                <ConcernDetail
                    concern={currentConcern}
                    score={getScoreValue(currentConcern.key)}
                    originalImage={
                        original_image ? `data:image/jpeg;base64,${original_image}` : null
                    }
                    maskImage={getMaskImage(currentConcern.key)}
                    concernOverlay={getConcernOverlay(currentConcern.key)}
                    compositeImage={
                        composite_image ? `data:image/jpeg;base64,${composite_image}` : null
                    }
                    analysisText={analysis_texts?.[currentConcern.key.replace('_v2', '')]}
                />
            </div>
        );
    };

    return (
        <div className="results-container">
            {/* Background gradient */}
            <div className="gradient-background" />

            <div className="results-content">
                {/* Header */}
                <h1 className="results-title">Analisis Kulit Komprehensif Anda</h1>

                {/* Main Tab Navigation */}
                <div className="main-tabs">
                    {MAIN_TABS.map((tab) => (
                        <button
                            key={tab.id}
                            className={`main-tab ${activeMainTab === tab.id ? 'active' : ''}`}
                            onClick={() => {
                                setActiveMainTab(tab.id);
                                setActiveSubTab(null);
                            }}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <div className="tab-content">
                    {activeMainTab === 'umum' ? renderLaporanUmum() : renderLaporanDetail()}
                </div>
            </div>
        </div>
    );
}
