export interface Translations {
  [key: string]: string;
}

export const TRANSLATIONS: { [lang: string]: Translations } = {
  en: {
    // Nav
    'nav.home': 'Home',
    'nav.services': 'Services',
    'nav.about': 'About',
    'nav.contact': 'Contact',
    'nav.getQuote': 'Get a Quote',

    // Hero
    'hero.badge': 'Trusted by 500+ businesses worldwide',
    'hero.title': 'Your Gateway to',
    'hero.titleHighlight': 'Global Trade',
    'hero.subtitle': 'We connect businesses across borders with reliable sourcing, logistics, and trade solutions. From raw materials to finished goods — we make international trading seamless.',
    'hero.cta': 'Start Trading Today',
    'hero.ctaSecondary': 'Our Services',
    'hero.stat1': 'Countries',
    'hero.stat2': 'Products Traded',
    'hero.stat3': 'Client Satisfaction',

    // Services
    'services.title': 'Our Services',
    'services.subtitle': 'Comprehensive trading solutions tailored for your business needs across the globe.',
    'services.import.title': 'Import & Export',
    'services.import.desc': 'End-to-end import and export services with customs clearance, documentation, and compliance management.',
    'services.sourcing.title': 'Global Sourcing',
    'services.sourcing.desc': 'Access verified suppliers worldwide. We handle quality inspection, negotiation, and supplier management.',
    'services.logistics.title': 'Logistics & Shipping',
    'services.logistics.desc': 'Integrated freight forwarding, warehousing, and last-mile delivery across all major trade routes.',
    'services.consulting.title': 'Trade Consulting',
    'services.consulting.desc': 'Expert guidance on trade regulations, tariffs, market entry strategies, and risk management.',
    'services.finance.title': 'Trade Finance',
    'services.finance.desc': 'Letters of credit, trade insurance, and flexible payment solutions to secure your transactions.',
    'services.digital.title': 'Digital Platform',
    'services.digital.desc': 'Real-time tracking, analytics dashboard, and digital documentation for full supply chain visibility.',

    // About
    'about.title': 'Why Choose GlobalTrade Pro?',
    'about.subtitle': 'With decades of experience in international trade, we deliver results that matter.',
    'about.years': 'Years Experience',
    'about.partners': 'Global Partners',
    'about.volume': 'Annual Volume',
    'about.support': 'Support',
    'about.supportValue': '24/7',
    'about.desc1': 'GlobalTrade Pro is a leading international trading company specializing in connecting businesses across continents. Our extensive network spans over 80 countries, providing unmatched access to global markets.',
    'about.desc2': 'We combine deep industry expertise with cutting-edge technology to streamline every aspect of international trade — from sourcing and procurement to logistics and compliance.',

    // Contact
    'contact.title': 'Get In Touch',
    'contact.subtitle': 'Ready to expand your business globally? Contact us for a free consultation.',
    'contact.name': 'Full Name',
    'contact.email': 'Email Address',
    'contact.company': 'Company Name',
    'contact.message': 'Tell us about your trading needs...',
    'contact.submit': 'Send Message',
    'contact.sending': 'Sending...',
    'contact.success': 'Message sent successfully! We\'ll get back to you within 24 hours.',
    'contact.error': 'Failed to send message. Please try again.',
    'contact.info.title': 'Contact Information',
    'contact.info.email': 'contact@globaltradepro.com',
    'contact.info.phone': '+1 (888) 555-0123',
    'contact.info.address': '100 Trade Center Blvd, Suite 500\nNew York, NY 10001, USA',
    'contact.info.hours': 'Mon - Fri: 9:00 AM - 6:00 PM (EST)',

    // Footer
    'footer.desc': 'Connecting businesses across borders with reliable international trading solutions.',
    'footer.quickLinks': 'Quick Links',
    'footer.services': 'Services',
    'footer.legal': 'Legal',
    'footer.privacy': 'Privacy Policy',
    'footer.terms': 'Terms of Service',
    'footer.cookie': 'Cookie Policy',
    'footer.copyright': '© 2026 GlobalTrade Pro. All rights reserved.',
  },
  zh: {
    // Nav
    'nav.home': '首页',
    'nav.services': '服务',
    'nav.about': '关于我们',
    'nav.contact': '联系我们',
    'nav.getQuote': '获取报价',

    // Hero
    'hero.badge': '全球500+企业的信赖之选',
    'hero.title': '您通往',
    'hero.titleHighlight': '全球贸易的桥梁',
    'hero.subtitle': '我们连接跨国企业，提供可靠的采购、物流和贸易解决方案。从原材料到成品——让国际贸易无缝衔接。',
    'hero.cta': '立即开始贸易',
    'hero.ctaSecondary': '我们的服务',
    'hero.stat1': '国家',
    'hero.stat2': '贸易产品',
    'hero.stat3': '客户满意度',

    // Services
    'services.title': '我们的服务',
    'services.subtitle': '为您的全球业务需求量身定制的综合贸易解决方案。',
    'services.import.title': '进出口贸易',
    'services.import.desc': '端到端进出口服务，包括清关、文件处理和合规管理。',
    'services.sourcing.title': '全球采购',
    'services.sourcing.desc': '连接全球认证供应商，负责质量检验、谈判和供应商管理。',
    'services.logistics.title': '物流与运输',
    'services.logistics.desc': '集成货运代理、仓储和末端配送，覆盖所有主要贸易路线。',
    'services.consulting.title': '贸易咨询',
    'services.consulting.desc': '提供贸易法规、关税、市场进入策略和风险管理的专业指导。',
    'services.finance.title': '贸易融资',
    'services.finance.desc': '信用证、贸易保险和灵活的支付方案，保障您的交易安全。',
    'services.digital.title': '数字化平台',
    'services.digital.desc': '实时追踪、分析仪表盘和数字化文档，实现全供应链可视化。',

    // About
    'about.title': '为什么选择 GlobalTrade Pro？',
    'about.subtitle': '凭借数十年的国际贸易经验，我们交付真正有价值的成果。',
    'about.years': '年经验',
    'about.partners': '全球合作伙伴',
    'about.volume': '年交易量',
    'about.support': '客户支持',
    'about.supportValue': '全天候',
    'about.desc1': 'GlobalTrade Pro 是一家领先的国际贸易公司，专注于连接各大洲的企业。我们的广泛网络覆盖80多个国家，提供无与伦比的全球市场准入。',
    'about.desc2': '我们将深厚的行业专业知识与尖端技术相结合，简化国际贸易的每一个环节——从采购到物流再到合规。',

    // Contact
    'contact.title': '联系我们',
    'contact.subtitle': '准备好将业务拓展到全球了吗？联系我们获取免费咨询。',
    'contact.name': '姓名',
    'contact.email': '电子邮箱',
    'contact.company': '公司名称',
    'contact.message': '请告诉我们您的贸易需求...',
    'contact.submit': '发送消息',
    'contact.sending': '发送中...',
    'contact.success': '消息发送成功！我们将在24小时内回复您。',
    'contact.error': '发送失败，请重试。',
    'contact.info.title': '联系方式',
    'contact.info.email': 'contact@globaltradepro.com',
    'contact.info.phone': '+86 400-888-0123',
    'contact.info.address': '中国上海市浦东新区\n陆家嘴金融贸易区100号',
    'contact.info.hours': '周一至周五: 9:00 - 18:00 (北京时间)',

    // Footer
    'footer.desc': '连接跨国企业，提供可靠的国际贸易解决方案。',
    'footer.quickLinks': '快速链接',
    'footer.services': '服务',
    'footer.legal': '法律信息',
    'footer.privacy': '隐私政策',
    'footer.terms': '服务条款',
    'footer.cookie': 'Cookie政策',
    'footer.copyright': '© 2026 GlobalTrade Pro. 版权所有。',
  },
  es: {
    // Nav
    'nav.home': 'Inicio',
    'nav.services': 'Servicios',
    'nav.about': 'Nosotros',
    'nav.contact': 'Contacto',
    'nav.getQuote': 'Cotización',

    // Hero
    'hero.badge': 'Confianza de más de 500 empresas en todo el mundo',
    'hero.title': 'Su puerta al',
    'hero.titleHighlight': 'Comercio Global',
    'hero.subtitle': 'Conectamos empresas a través de fronteras con soluciones confiables de abastecimiento, logística y comercio. De materias primas a productos terminados — hacemos el comercio internacional sin complicaciones.',
    'hero.cta': 'Comience a Comerciar Hoy',
    'hero.ctaSecondary': 'Nuestros Servicios',
    'hero.stat1': 'Países',
    'hero.stat2': 'Productos',
    'hero.stat3': 'Satisfacción',

    // Services
    'services.title': 'Nuestros Servicios',
    'services.subtitle': 'Soluciones comerciales integrales adaptadas a las necesidades de su negocio en todo el mundo.',
    'services.import.title': 'Importación y Exportación',
    'services.import.desc': 'Servicios de importación y exportación de principio a fin con despacho aduanero, documentación y gestión de cumplimiento.',
    'services.sourcing.title': 'Abastecimiento Global',
    'services.sourcing.desc': 'Acceda a proveedores verificados en todo el mundo. Gestionamos inspección de calidad, negociación y gestión de proveedores.',
    'services.logistics.title': 'Logística y Envío',
    'services.logistics.desc': 'Envío de carga integrado, almacenamiento y entrega de última milla en todas las rutas comerciales principales.',
    'services.consulting.title': 'Consultoría Comercial',
    'services.consulting.desc': 'Orientación experta en regulaciones comerciales, aranceles, estrategias de entrada al mercado y gestión de riesgos.',
    'services.finance.title': 'Finanzas Comerciales',
    'services.finance.desc': 'Cartas de crédito, seguros comerciales y soluciones de pago flexibles para asegurar sus transacciones.',
    'services.digital.title': 'Plataforma Digital',
    'services.digital.desc': 'Seguimiento en tiempo real, panel de análisis y documentación digital para visibilidad total de la cadena de suministro.',

    // About
    'about.title': '¿Por qué elegir GlobalTrade Pro?',
    'about.subtitle': 'Con décadas de experiencia en comercio internacional, entregamos resultados que importan.',
    'about.years': 'Años de Experiencia',
    'about.partners': 'Socios Globales',
    'about.volume': 'Volumen Anual',
    'about.support': 'Soporte',
    'about.supportValue': '24/7',
    'about.desc1': 'GlobalTrade Pro es una empresa líder en comercio internacional especializada en conectar negocios entre continentes. Nuestra extensa red abarca más de 80 países, brindando acceso incomparable a los mercados globales.',
    'about.desc2': 'Combinamos profunda experiencia en la industria con tecnología de vanguardia para optimizar cada aspecto del comercio internacional — desde el abastecimiento y la adquisición hasta la logística y el cumplimiento.',

    // Contact
    'contact.title': 'Contáctenos',
    'contact.subtitle': '¿Listo para expandir su negocio globalmente? Contáctenos para una consulta gratuita.',
    'contact.name': 'Nombre Completo',
    'contact.email': 'Correo Electrónico',
    'contact.company': 'Nombre de la Empresa',
    'contact.message': 'Cuéntenos sobre sus necesidades comerciales...',
    'contact.submit': 'Enviar Mensaje',
    'contact.sending': 'Enviando...',
    'contact.success': '¡Mensaje enviado con éxito! Le responderemos dentro de 24 horas.',
    'contact.error': 'Error al enviar el mensaje. Por favor, inténtelo de nuevo.',
    'contact.info.title': 'Información de Contacto',
    'contact.info.email': 'contact@globaltradepro.com',
    'contact.info.phone': '+34 900 555 0123',
    'contact.info.address': 'Paseo de la Castellana 100\n28046 Madrid, España',
    'contact.info.hours': 'Lun - Vie: 9:00 - 18:00 (CET)',

    // Footer
    'footer.desc': 'Conectando empresas a través de fronteras con soluciones comerciales internacionales confiables.',
    'footer.quickLinks': 'Enlaces Rápidos',
    'footer.services': 'Servicios',
    'footer.legal': 'Legal',
    'footer.privacy': 'Política de Privacidad',
    'footer.terms': 'Términos de Servicio',
    'footer.cookie': 'Política de Cookies',
    'footer.copyright': '© 2026 GlobalTrade Pro. Todos los derechos reservados.',
  },
};

export const SUPPORTED_LANGUAGES = [
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'zh', label: '中文', flag: '🇨🇳' },
  { code: 'es', label: 'Español', flag: '🇪🇸' },
];

export const DEFAULT_LANGUAGE = 'en';
