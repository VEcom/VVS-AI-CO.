-- schema.sql — 리조트피플 리플렛 플랫폼 (MySQL 8)
-- 관리자 권한 2단계(본사/지점)와 지점 확장을 데이터 모델 수준에서 지원.
SET NAMES utf8mb4;

-- ── 지점 (지점 확장 = INSERT 한 줄. 구조 변경 불필요) ──
CREATE TABLE branches (
  id           VARCHAR(32)  PRIMARY KEY,           -- 'mapo', 'gangnam' ...
  name         VARCHAR(64)  NOT NULL,
  status       ENUM('운영중','사전예약','준비중') NOT NULL DEFAULT '준비중',
  headline     VARCHAR(255),
  open_date    VARCHAR(32),
  address      VARCHAR(255),
  area         VARCHAR(255),
  hero_style   VARCHAR(255),
  signature    VARCHAR(255),
  content_json JSON,                                -- 트레이너·시간표·이벤트·마일스톤 (지점별 차별화)
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ── 브랜드 공통요소 (본사만 편집) ──
CREATE TABLE brand_settings (
  id           INT PRIMARY KEY DEFAULT 1,
  name         VARCHAR(64),
  tagline      VARCHAR(255),
  intro        TEXT,
  contents_json JSON,                               -- 콘텐츠 카테고리
  incentive_json JSON,                              -- 인센티브 정책
  privacy_json JSON,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ── 관리자 (role 로 2단계 권한 구분) ──
CREATE TABLE admins (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  email        VARCHAR(128) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role         ENUM('hq','branch') NOT NULL,        -- hq=본사(전체), branch=지점
  branch_id    VARCHAR(32) NULL,                    -- role='branch' 일 때 소속 지점
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_admin_branch FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- ── 리드(문의) ──
CREATE TABLE leads (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  branch_id    VARCHAR(32) NOT NULL,
  name         VARCHAR(64) NOT NULL,
  phone        VARCHAR(32) NOT NULL,
  program      VARCHAR(64),
  source       VARCHAR(64),                         -- 유입 경로
  marketing_agree TINYINT(1) DEFAULT 0,
  utm_source   VARCHAR(64), utm_medium VARCHAR(64),
  utm_campaign VARCHAR(64), utm_term VARCHAR(64), utm_content VARCHAR(64),
  referrer_id  BIGINT NULL,                         -- 추천(링크공유) 인센티브 추적
  status       ENUM('신규','상담','방문','전환','보류') DEFAULT '신규',
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_leads_branch (branch_id, created_at),
  CONSTRAINT fk_lead_branch FOREIGN KEY (branch_id) REFERENCES branches(id)
);
