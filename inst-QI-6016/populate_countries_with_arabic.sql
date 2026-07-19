PRAGMA foreign_keys = OFF;

-- Step 1: Ensure the countries table has the 'name_ar' column.
-- This section re-creates the table if 'name_ar' is missing, preserving existing 'name' data.
BEGIN TRANSACTION;

-- Create a temporary table with the desired schema including 'name_ar'
CREATE TABLE IF NOT EXISTS countries_temp (
    country_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    name_ar TEXT
);

-- Copy existing data from the old table to the new table.
-- If 'name_ar' exists in the old table (unlikely based on user's report), it would also be copied.
INSERT OR IGNORE INTO countries_temp (country_id, name)
SELECT country_id, name FROM countries;

-- Drop the old table
DROP TABLE IF EXISTS countries;

-- Rename the temporary table to the original table name
ALTER TABLE countries_temp RENAME TO countries;

COMMIT;

-- Step 2: Update existing countries to add Arabic names.
-- This is crucial for countries that were already in the database before this script ran.
-- We use UPDATE WHERE name = ? to match existing English names and fill in name_ar.

UPDATE countries SET name_ar = 'أفغانستان' WHERE name = 'Afghanistan';
UPDATE countries SET name_ar = 'ألبانيا' WHERE name = 'Albania';
UPDATE countries SET name_ar = 'الجزائر' WHERE name = 'Algeria';
UPDATE countries SET name_ar = 'أندورا' WHERE name = 'Andorra';
UPDATE countries SET name_ar = 'أنجولا' WHERE name = 'Angola';
UPDATE countries SET name_ar = 'أنتيغوا وباربودا' WHERE name = 'Antigua and Barbuda';
UPDATE countries SET name_ar = 'الأرجنتين' WHERE name = 'Argentina';
UPDATE countries SET name_ar = 'أرمينيا' WHERE name = 'Armenia';
UPDATE countries SET name_ar = 'أستراليا' WHERE name = 'Australia';
UPDATE countries SET name_ar = 'النمسا' WHERE name = 'Austria';
UPDATE countries SET name_ar = 'أذربيجان' WHERE name = 'Azerbaijan';
UPDATE countries SET name_ar = 'جزر البهاما' WHERE name = 'Bahamas';
UPDATE countries SET name_ar = 'البحرين' WHERE name = 'Bahrain';
UPDATE countries SET name_ar = 'بنغلاديش' WHERE name = 'Bangladesh';
UPDATE countries SET name_ar = 'بربادوس' WHERE name = 'Barbados';
UPDATE countries SET name_ar = 'بيلاروسيا' WHERE name = 'Belarus';
UPDATE countries SET name_ar = 'بلجيكا' WHERE name = 'Belgium';
UPDATE countries SET name_ar = 'بليز' WHERE name = 'Belize';
UPDATE countries SET name_ar = 'بنين' WHERE name = 'Benin';
UPDATE countries SET name_ar = 'بوتان' WHERE name = 'Bhutan';
UPDATE countries SET name_ar = 'بوليفيا' WHERE name = 'Bolivia';
UPDATE countries SET name_ar = 'البوسنة والهرسك' WHERE name = 'Bosnia and Herzegovina';
UPDATE countries SET name_ar = 'بوتسوانا' WHERE name = 'Botswana';
UPDATE countries SET name_ar = 'البرازيل' WHERE name = 'Brazil';
UPDATE countries SET name_ar = 'بروناي' WHERE name = 'Brunei';
UPDATE countries SET name_ar = 'بلغاريا' WHERE name = 'Bulgaria';
UPDATE countries SET name_ar = 'بوركينا فاسو' WHERE name = 'Burkina Faso';
UPDATE countries SET name_ar = 'بوروندي' WHERE name = 'Burundi';
UPDATE countries SET name_ar = 'الرأس الأخضر' WHERE name = 'Cabo Verde';
UPDATE countries SET name_ar = 'كمبوديا' WHERE name = 'Cambodia';
UPDATE countries SET name_ar = 'الكاميرون' WHERE name = 'Cameroon';
UPDATE countries SET name_ar = 'كندا' WHERE name = 'Canada';
UPDATE countries SET name_ar = 'جمهورية أفريقيا الوسطى' WHERE name = 'Central African Republic';
UPDATE countries SET name_ar = 'تشاد' WHERE name = 'Chad';
UPDATE countries SET name_ar = 'تشيلي' WHERE name = 'Chile';
UPDATE countries SET name_ar = 'الصين' WHERE name = 'China';
UPDATE countries SET name_ar = 'كولومبيا' WHERE name = 'Colombia';
UPDATE countries SET name_ar = 'جزر القمر' WHERE name = 'Comoros';
UPDATE countries SET name_ar = 'الكونغو (برازافيل)' WHERE name = 'Congo (Brazzaville)';
UPDATE countries SET name_ar = 'الكونغو (كينشاسا)' WHERE name = 'Congo (Kinshasa)';
UPDATE countries SET name_ar = 'كوستاريكا' WHERE name = 'Costa Rica';
UPDATE countries SET name_ar = 'كرواتيا' WHERE name = 'Croatia';
UPDATE countries SET name_ar = 'كوبا' WHERE name = 'Cuba';
UPDATE countries SET name_ar = 'قبرص' WHERE name = 'Cyprus';
UPDATE countries SET name_ar = 'التشيك' WHERE name = 'Czechia';
UPDATE countries SET name_ar = 'الدنمارك' WHERE name = 'Denmark';
UPDATE countries SET name_ar = 'جيبوتي' WHERE name = 'Djibouti';
UPDATE countries SET name_ar = 'دومينيكا' WHERE name = 'Dominica';
UPDATE countries SET name_ar = 'جمهورية الدومينيكان' WHERE name = 'Dominican Republic';
UPDATE countries SET name_ar = 'الإكوادور' WHERE name = 'Ecuador';
UPDATE countries SET name_ar = 'مصر' WHERE name = 'Egypt';
UPDATE countries SET name_ar = 'السلفادور' WHERE name = 'El Salvador';
UPDATE countries SET name_ar = 'غينيا الاستوائية' WHERE name = 'Equatorial Guinea';
UPDATE countries SET name_ar = 'إريتريا' WHERE name = 'Eritrea';
UPDATE countries SET name_ar = 'إستونيا' WHERE name = 'Estonia';
UPDATE countries SET name_ar = 'إسواتيني' WHERE name = 'Eswatini';
UPDATE countries SET name_ar = 'إثيوبيا' WHERE name = 'Ethiopia';
UPDATE countries SET name_ar = 'فيجي' WHERE name = 'Fiji';
UPDATE countries SET name_ar = 'فنلندا' WHERE name = 'Finland';
UPDATE countries SET name_ar = 'فرنسا' WHERE name = 'France';
UPDATE countries SET name_ar = 'الجابون' WHERE name = 'Gabon';
UPDATE countries SET name_ar = 'غامبيا' WHERE name = 'Gambia';
UPDATE countries SET name_ar = 'جورجيا' WHERE name = 'Georgia';
UPDATE countries SET name_ar = 'ألمانيا' WHERE name = 'Germany';
UPDATE countries SET name_ar = 'غانا' WHERE name = 'Ghana';
UPDATE countries SET name_ar = 'اليونان' WHERE name = 'Greece';
UPDATE countries SET name_ar = 'غرينادا' WHERE name = 'Grenada';
UPDATE countries SET name_ar = 'غواتيمالا' WHERE name = 'Guatemala';
UPDATE countries SET name_ar = 'غينيا' WHERE name = 'Guinea';
UPDATE countries SET name_ar = 'غينيا بيساو' WHERE name = 'Guinea-Bissau';
UPDATE countries SET name_ar = 'غيانا' WHERE name = 'Guyana';
UPDATE countries SET name_ar = 'هايتي' WHERE name = 'Haiti';
UPDATE countries SET name_ar = 'هندوراس' WHERE name = 'Honduras';
UPDATE countries SET name_ar = 'المجر' WHERE name = 'Hungary';
UPDATE countries SET name_ar = 'أيسلندا' WHERE name = 'Iceland';
UPDATE countries SET name_ar = 'الهند' WHERE name = 'India';
UPDATE countries SET name_ar = 'إندونيسيا' WHERE name = 'Indonesia';
UPDATE countries SET name_ar = 'إيران' WHERE name = 'Iran';
UPDATE countries SET name_ar = 'العراق' WHERE name = 'Iraq';
UPDATE countries SET name_ar = 'أيرلندا' WHERE name = 'Ireland';
UPDATE countries SET name_ar = 'إسرائيل' WHERE name = 'Israel';
UPDATE countries SET name_ar = 'إيطاليا' WHERE name = 'Italy';
UPDATE countries SET name_ar = 'ساحل العاج' WHERE name = 'Ivory Coast';
UPDATE countries SET name_ar = 'جامايكا' WHERE name = 'Jamaica';
UPDATE countries SET name_ar = 'اليابان' WHERE name = 'Japan';
UPDATE countries SET name_ar = 'الأردن' WHERE name = 'Jordan';
UPDATE countries SET name_ar = 'كازاخستان' WHERE name = 'Kazakhstan';
UPDATE countries SET name_ar = 'كينيا' WHERE name = 'Kenya';
UPDATE countries SET name_ar = 'كيريباتي' WHERE name = 'Kiribati';
UPDATE countries SET name_ar = 'الكويت' WHERE name = 'Kuwait';
UPDATE countries SET name_ar = 'قيرغيزستان' WHERE name = 'Kyrgyzstan';
UPDATE countries SET name_ar = 'لاوس' WHERE name = 'Laos';
UPDATE countries SET name_ar = 'لاتفيا' WHERE name = 'Latvia';
UPDATE countries SET name_ar = 'لبنان' WHERE name = 'Lebanon';
UPDATE countries SET name_ar = 'ليسوتو' WHERE name = 'Lesotho';
UPDATE countries SET name_ar = 'ليبيريا' WHERE name = 'Liberia';
UPDATE countries SET name_ar = 'ليبيا' WHERE name = 'Libya';
UPDATE countries SET name_ar = 'ليختنشتاين' WHERE name = 'Liechtenstein';
UPDATE countries SET name_ar = 'ليتوانيا' WHERE name = 'Lithuania';
UPDATE countries SET name_ar = 'لوكسمبورغ' WHERE name = 'Luxembourg';
UPDATE countries SET name_ar = 'مدغشقر' WHERE name = 'Madagascar';
UPDATE countries SET name_ar = 'مالاوي' WHERE name = 'Malawi';
UPDATE countries SET name_ar = 'ماليزيا' WHERE name = 'Malaysia';
UPDATE countries SET name_ar = 'جزر المالديف' WHERE name = 'Maldives';
UPDATE countries SET name_ar = 'مالي' WHERE name = 'Mali';
UPDATE countries SET name_ar = 'مالطا' WHERE name = 'Malta';
UPDATE countries SET name_ar = 'جزر مارشال' WHERE name = 'Marshall Islands';
UPDATE countries SET name_ar = 'موريتانيا' WHERE name = 'Mauritania';
UPDATE countries SET name_ar = 'موريشيوس' WHERE name = 'Mauritius';
UPDATE countries SET name_ar = 'المكسيك' WHERE name = 'Mexico';
UPDATE countries SET name_ar = 'ميكرونيزيا' WHERE name = 'Micronesia';
UPDATE countries SET name_ar = 'مولدوفا' WHERE name = 'Moldova';
UPDATE countries SET name_ar = 'موناكو' WHERE name = 'Monaco';
UPDATE countries SET name_ar = 'منغوليا' WHERE name = 'Mongolia';
UPDATE countries SET name_ar = 'الجبل الأسود' WHERE name = 'Montenegro';
UPDATE countries SET name_ar = 'المغرب' WHERE name = 'Morocco';
UPDATE countries SET name_ar = 'موزمبيق' WHERE name = 'Mozambique';
UPDATE countries SET name_ar = 'ميانمار' WHERE name = 'Myanmar';
UPDATE countries SET name_ar = 'ناميبيا' WHERE name = 'Namibia';
UPDATE countries SET name_ar = 'ناورو' WHERE name = 'Nauru';
UPDATE countries SET name_ar = 'نيبال' WHERE name = 'Nepal';
UPDATE countries SET name_ar = 'هولندا' WHERE name = 'Netherlands';
UPDATE countries SET name_ar = 'نيوزيلندا' WHERE name = 'New Zealand';
UPDATE countries SET name_ar = 'نيكاراغوا' WHERE name = 'Nicaragua';
UPDATE countries SET name_ar = 'النيجر' WHERE name = 'Niger';
UPDATE countries SET name_ar = 'نيجيريا' WHERE name = 'Nigeria';
UPDATE countries SET name_ar = 'كوريا الشمالية' WHERE name = 'North Korea';
UPDATE countries SET name_ar = 'مقدونيا الشمالية' WHERE name = 'North Macedonia';
UPDATE countries SET name_ar = 'النرويج' WHERE name = 'Norway';
UPDATE countries SET name_ar = 'عمان' WHERE name = 'Oman';
UPDATE countries SET name_ar = 'باكستان' WHERE name = 'Pakistan';
UPDATE countries SET name_ar = 'بالاو' WHERE name = 'Palau';
UPDATE countries SET name_ar = 'فلسطين' WHERE name = 'Palestine';
UPDATE countries SET name_ar = 'بنما' WHERE name = 'Panama';
UPDATE countries SET name_ar = 'بابوا غينيا الجديدة' WHERE name = 'Papua New Guinea';
UPDATE countries SET name_ar = 'باراغواي' WHERE name = 'Paraguay';
UPDATE countries SET name_ar = 'بيرو' WHERE name = 'Peru';
UPDATE countries SET name_ar = 'الفلبين' WHERE name = 'Philippines';
UPDATE countries SET name_ar = 'بولندا' WHERE name = 'Poland';
UPDATE countries SET name_ar = 'البرتغال' WHERE name = 'Portugal';
UPDATE countries SET name_ar = 'قطر' WHERE name = 'Qatar';
UPDATE countries SET name_ar = 'رومانيا' WHERE name = 'Romania';
UPDATE countries SET name_ar = 'روسيا' WHERE name = 'Russia';
UPDATE countries SET name_ar = 'رواندا' WHERE name = 'Rwanda';
UPDATE countries SET name_ar = 'سانت كيتس ونيفيس' WHERE name = 'Saint Kitts and Nevis';
UPDATE countries SET name_ar = 'سانت لوسيا' WHERE name = 'Saint Lucia';
UPDATE countries SET name_ar = 'سانت فنسنت والغرينادين' WHERE name = 'Saint Vincent and the Grenadines';
UPDATE countries SET name_ar = 'ساموا' WHERE name = 'Samoa';
UPDATE countries SET name_ar = 'سان مارينو' WHERE name = 'San Marino';
UPDATE countries SET name_ar = 'ساو تومي وبرينسيبي' WHERE name = 'Sao Tome and Principe';
UPDATE countries SET name_ar = 'المملكة العربية السعودية' WHERE name = 'Saudi Arabia';
UPDATE countries SET name_ar = 'السنغال' WHERE name = 'Senegal';
UPDATE countries SET name_ar = 'صربيا' WHERE name = 'Serbia';
UPDATE countries SET name_ar = 'سيشل' WHERE name = 'Seychelles';
UPDATE countries SET name_ar = 'سيراليون' WHERE name = 'Sierra Leone';
UPDATE countries SET name_ar = 'سنغافورة' WHERE name = 'Singapore';
UPDATE countries SET name_ar = 'سلوفاكيا' WHERE name = 'Slovakia';
UPDATE countries SET name_ar = 'سلوفينيا' WHERE name = 'Slovenia';
UPDATE countries SET name_ar = 'جزر سليمان' WHERE name = 'Solomon Islands';
UPDATE countries SET name_ar = 'الصومال' WHERE name = 'Somalia';
UPDATE countries SET name_ar = 'جنوب أفريقيا' WHERE name = 'South Africa';
UPDATE countries SET name_ar = 'كوريا الجنوبية' WHERE name = 'South Korea';
UPDATE countries SET name_ar = 'جنوب السودان' WHERE name = 'South Sudan';
UPDATE countries SET name_ar = 'إسبانيا' WHERE name = 'Spain';
UPDATE countries SET name_ar = 'سري لانكا' WHERE name = 'Sri Lanka';
UPDATE countries SET name_ar = 'السودان' WHERE name = 'Sudan';
UPDATE countries SET name_ar = 'سورينام' WHERE name = 'Suriname';
UPDATE countries SET name_ar = 'السويد' WHERE name = 'Sweden';
UPDATE countries SET name_ar = 'سويسرا' WHERE name = 'Switzerland';
UPDATE countries SET name_ar = 'سوريا' WHERE name = 'Syria';
UPDATE countries SET name_ar = 'تايوان' WHERE name = 'Taiwan';
UPDATE countries SET name_ar = 'طاجيكستان' WHERE name = 'Tajikistan';
UPDATE countries SET name_ar = 'تنزانيا' WHERE name = 'Tanzania';
UPDATE countries SET name_ar = 'تايلاند' WHERE name = 'Thailand';
UPDATE countries SET name_ar = 'تيمور الشرقية' WHERE name = 'Timor-Leste';
UPDATE countries SET name_ar = 'توغو' WHERE name = 'Togo';
UPDATE countries SET name_ar = 'تونغا' WHERE name = 'Tonga';
UPDATE countries SET name_ar = 'ترينيداد وتوباغو' WHERE name = 'Trinidad and Tobago';
UPDATE countries SET name_ar = 'تونس' WHERE name = 'Tunisia';
UPDATE countries SET name_ar = 'تركيا' WHERE name = 'Turkey';
UPDATE countries SET name_ar = 'تركمانستان' WHERE name = 'Turkmenistan';
UPDATE countries SET name_ar = 'توفالو' WHERE name = 'Tuvalu';
UPDATE countries SET name_ar = 'أوغندا' WHERE name = 'Uganda';
UPDATE countries SET name_ar = 'أوكرانيا' WHERE name = 'Ukraine';
UPDATE countries SET name_ar = 'الإمارات العربية المتحدة' WHERE name = 'United Arab Emirates';
UPDATE countries SET name_ar = 'المملكة المتحدة' WHERE name = 'United Kingdom';
UPDATE countries SET name_ar = 'الولايات المتحدة' WHERE name = 'United States';
UPDATE countries SET name_ar = 'أوروغواي' WHERE name = 'Uruguay';
UPDATE countries SET name_ar = 'أوزبكستان' WHERE name = 'Uzbekistan';
UPDATE countries SET name_ar = 'فانواتو' WHERE name = 'Vanuatu';
UPDATE countries SET name_ar = 'مدينة الفاتيكان' WHERE name = 'Vatican City';
UPDATE countries SET name_ar = 'فنزويلا' WHERE name = 'Venezuela';
UPDATE countries SET name_ar = 'فيتنام' WHERE name = 'Vietnam';
UPDATE countries SET name_ar = 'اليمن' WHERE name = 'Yemen';
UPDATE countries SET name_ar = 'زامبيا' WHERE name = 'Zambia';
UPDATE countries SET name_ar = 'زيمبابوي' WHERE name = 'Zimbabwe';

-- Step 3: Insert any missing countries (that were not in the original table)
-- This ensures that if the user's original table was very sparse, all countries are present.
-- This part is the same as the INSERT OR IGNORE section from the previous script.
INSERT OR IGNORE INTO countries (country_id, name, name_ar) VALUES
(1, 'Afghanistan', 'أفغانستان'),
(2, 'Albania', 'ألبانيا'),
(3, 'Algeria', 'الجزائر'),
(4, 'Andorra', 'أندورا'),
(5, 'Angola', 'أنجولا'),
(6, 'Antigua and Barbuda', 'أنتيغوا وباربودا'),
(7, 'Argentina', 'الأرجنتين'),
(8, 'Armenia', 'أرمينيا'),
(9, 'Australia', 'أستراليا'),
(10, 'Austria', 'النمسا'),
(11, 'Azerbaijan', 'أذربيجان'),
(12, 'Bahamas', 'جزر البهاما'),
(13, 'Bahrain', 'البحرين'),
(14, 'Bangladesh', 'بنغلاديش'),
(15, 'Barbados', 'بربادوس'),
(16, 'Belarus', 'بيلاروسيا'),
(17, 'Belgium', 'بلجيكا'),
(18, 'Belize', 'بليز'),
(19, 'Benin', 'بنين'),
(20, 'Bhutan', 'بوتان'),
(21, 'Bolivia', 'بوليفيا'),
(22, 'Bosnia and Herzegovina', 'البوسنة والهرسك'),
(23, 'Botswana', 'بوتسوانا'),
(24, 'Brazil', 'البرازيل'),
(25, 'Brunei', 'بروناي'),
(26, 'Bulgaria', 'بلغاريا'),
(27, 'Burkina Faso', 'بوركينا فاسو'),
(28, 'Burundi', 'بوروندي'),
(29, 'Cabo Verde', 'الرأس الأخضر'),
(30, 'Cambodia', 'كمبوديا'),
(31, 'Cameroon', 'الكاميرون'),
(32, 'Canada', 'كندا'),
(33, 'Central African Republic', 'جمهورية أفريقيا الوسطى'),
(34, 'Chad', 'تشاد'),
(35, 'Chile', 'تشيلي'),
(36, 'China', 'الصين'),
(37, 'Colombia', 'كولومبيا'),
(38, 'Comoros', 'جزر القمر'),
(39, 'Congo (Brazzaville)', 'الكونغو (برازافيل)'),
(40, 'Congo (Kinshasa)', 'الكونغو (كينشاسا)'),
(41, 'Costa Rica', 'كوستاريكا'),
(42, 'Croatia', 'كرواتيا'),
(43, 'Cuba', 'كوبا'),
(44, 'Cyprus', 'قبرص'),
(45, 'Czechia', 'التشيك'),
(46, 'Denmark', 'الدنمارك'),
(47, 'Djibouti', 'جيبوتي'),
(48, 'Dominica', 'دومينيكا'),
(49, 'Dominican Republic', 'جمهورية الدومينيكان'),
(50, 'Ecuador', 'الإكوادور'),
(51, 'Egypt', 'مصر'),
(52, 'El Salvador', 'السلفادور'),
(53, 'Equatorial Guinea', 'غينيا الاستوائية'),
(54, 'Eritrea', 'إريتريا'),
(55, 'Estonia', 'إستونيا'),
(56, 'Eswatini', 'إسواتيني'),
(57, 'Ethiopia', 'إثيوبيا'),
(58, 'Fiji', 'فيجي'),
(59, 'Finland', 'فنلندا'),
(60, 'France', 'فرنسا'),
(61, 'Gabon', 'الجابون'),
(62, 'Gambia', 'غامبيا'),
(63, 'Georgia', 'جورجيا'),
(64, 'Germany', 'ألمانيا'),
(65, 'Ghana', 'غانا'),
(66, 'Greece', 'اليونان'),
(67, 'Grenada', 'غرينادا'),
(68, 'Guatemala', 'غواتيمالا'),
(69, 'Guinea', 'غينيا'),
(70, 'Guinea-Bissau', 'غينيا بيساو'),
(71, 'Guyana', 'غيانا'),
(72, 'Haiti', 'هايتي'),
(73, 'Honduras', 'هندوراس'),
(74, 'Hungary', 'المجر'),
(75, 'Iceland', 'أيسلندا'),
(76, 'India', 'الهند'),
(77, 'Indonesia', 'إندونيسيا'),
(78, 'Iran', 'إيران'),
(79, 'Iraq', 'العراق'),
(80, 'Ireland', 'أيرلندا'),
(81, 'Israel', 'إسرائيل'),
(82, 'Italy', 'إيطاليا'),
(83, 'Ivory Coast', 'ساحل العاج'),
(84, 'Jamaica', 'جامايكا'),
(85, 'Japan', 'اليابان'),
(86, 'Jordan', 'الأردن'),
(87, 'Kazakhstan', 'كازاخستان'),
(88, 'Kenya', 'كينيا'),
(89, 'Kiribati', 'كيريباتي'),
(90, 'Kuwait', 'الكويت'),
(91, 'Kyrgyzstan', 'قيرغيزستان'),
(92, 'Laos', 'لاوس'),
(93, 'Latvia', 'لاتفيا'),
(94, 'Lebanon', 'لبنان'),
(95, 'Lesotho', 'ليسوتو'),
(96, 'Liberia', 'ليبيريا'),
(97, 'Libya', 'ليبيا'),
(98, 'Liechtenstein', 'ليختنشتاين'),
(99, 'Lithuania', 'ليتوانيا'),
(100, 'Luxembourg', 'لوكسمبورغ'),
(101, 'Madagascar', 'مدغشقر'),
(102, 'Malawi', 'مالاوي'),
(103, 'Malaysia', 'ماليزيا'),
(104, 'Maldives', 'جزر المالديف'),
(105, 'Mali', 'مالي'),
(106, 'Malta', 'مالطا'),
(107, 'Marshall Islands', 'جزر مارشال'),
(108, 'Mauritania', 'موريتانيا'),
(109, 'Mauritius', 'موريشيوس'),
(110, 'Mexico', 'المكسيك'),
(111, 'Micronesia', 'ميكرونيزيا'),
(112, 'Moldova', 'مولدوفا'),
(113, 'Monaco', 'موناكو'),
(114, 'Mongolia', 'منغوليا'),
(115, 'Montenegro', 'الجبل الأسود'),
(116, 'Morocco', 'المغرب'),
(117, 'Mozambique', 'موزمبيق'),
(118, 'Myanmar', 'ميانمار'),
(119, 'Namibia', 'ناميبيا'),
(120, 'Nauru', 'ناورو'),
(121, 'Nepal', 'نيبال'),
(122, 'Netherlands', 'هولندا'),
(123, 'New Zealand', 'نيوزيلندا'),
(124, 'Nicaragua', 'نيكاراغوا'),
(125, 'Niger', 'النيجر'),
(126, 'Nigeria', 'نيجيريا'),
(127, 'North Korea', 'كوريا الشمالية'),
(128, 'North Macedonia', 'مقدونيا الشمالية'),
(129, 'Norway', 'النرويج'),
(130, 'Oman', 'عمان'),
(131, 'Pakistan', 'باكستان'),
(132, 'Palau', 'بالاو'),
(133, 'Palestine', 'فلسطين'),
(134, 'Panama', 'بنما'),
(135, 'Papua New Guinea', 'بابوا غينيا الجديدة'),
(136, 'Paraguay', 'باراغواي'),
(137, 'Peru', 'بيرو'),
(138, 'Philippines', 'الفلبين'),
(139, 'Poland', 'بولندا'),
(140, 'Portugal', 'البرتغال'),
(141, 'Qatar', 'قطر'),
(142, 'Romania', 'رومانيا'),
(143, 'Russia', 'روسيا'),
(144, 'Rwanda', 'رواندا'),
(145, 'Saint Kitts and Nevis', 'سانت كيتس ونيفيس'),
(146, 'Saint Lucia', 'سانت لوسيا'),
(147, 'Saint Vincent and the Grenadines', 'سانت فنسنت والغرينادين'),
(148, 'Samoa', 'ساموا'),
(149, 'San Marino', 'سان مارينو'),
(150, 'Sao Tome and Principe', 'ساو تومي وبرينسيبي'),
(151, 'Saudi Arabia', 'المملكة العربية السعودية'),
(152, 'Senegal', 'السنغال'),
(153, 'Serbia', 'صربيا'),
(154, 'Seychelles', 'سيشل'),
(155, 'Sierra Leone', 'سيراليون'),
(156, 'Singapore', 'سنغافورة'),
(157, 'Slovakia', 'سلوفاكيا'),
(158, 'Slovenia', 'سلوفينيا'),
(159, 'Solomon Islands', 'جزر سليمان'),
(160, 'Somalia', 'الصومال'),
(161, 'South Africa', 'جنوب أفريقيا'),
(162, 'South Korea', 'كوريا الجنوبية'),
(163, 'South Sudan', 'جنوب السودان'),
(164, 'Spain', 'إسبانيا'),
(165, 'Sri Lanka', 'سري لانكا'),
(166, 'Sudan', 'السودان'),
(167, 'Suriname', 'سورينام'),
(168, 'Sweden', 'السويد'),
(169, 'Switzerland', 'سويسرا'),
(170, 'Syria', 'سوريا'),
(171, 'Taiwan', 'تايوان'),
(172, 'Tajikistan', 'طاجيكستان'),
(173, 'Tanzania', 'تنزانيا'),
(174, 'Thailand', 'تايلاند'),
(175, 'Timor-Leste', 'تيمور الشرقية'),
(176, 'Togo', 'توغو'),
(177, 'Tonga', 'تونغا'),
(178, 'Trinidad and Tobago', 'ترينيداد وتوباغو'),
(179, 'Tunisia', 'تونس'),
(180, 'Turkey', 'تركيا'),
(181, 'Turkmenistan', 'تركمانستان'),
(182, 'Tuvalu', 'توفالو'),
(183, 'Uganda', 'أوغندا'),
(184, 'Ukraine', 'أوكرانيا'),
(185, 'United Arab Emirates', 'الإمارات العربية المتحدة'),
(186, 'United Kingdom', 'المملكة المتحدة'),
(187, 'United States', 'الولايات المتحدة'),
(188, 'Uruguay', 'أوروغواي'),
(189, 'Uzbekistan', 'أوزبكستان'),
(190, 'Vanuatu', 'فانواتو'),
(191, 'Vatican City', 'مدينة الفاتيكان'),
(192, 'Venezuela', 'فنزويلا'),
(193, 'Vietnam', 'فيتنام'),
(194, 'Yemen', 'اليمن'),
(195, 'Zambia', 'زامبيا'),
(196, 'Zimbabwe', 'زيمبابوي');

PRAGMA foreign_keys = ON;