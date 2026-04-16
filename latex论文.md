\documentclass[12pt, a4paper]{article}
\usepackage{ctex}
\usepackage{geometry}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{hyperref}
\usepackage{setspace}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{caption}

\geometry{top=2.5cm, bottom=2.5cm, left=3cm, right=3cm}
\setstretch{1.5}

\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{\thesubsubsection}{1em}{}

\captionsetup{font=small, labelfont=bf}

\title{\textbf{足球转会数据管理与分析平台}\\[0.5em]
\large 数据库课程大作业报告}
\author{}
\date{}

\begin{document}

\maketitle
\tableofcontents
\newpage

% ============================================================
\section{第一阶段：选题}
% ============================================================

\subsection{选题背景}

足球转会市场是全球体育产业中规模最大、信息最密集的领域之一。每个转会窗口期间，数以千计的球员在全球各大联赛俱乐部之间流动，涉及转会费、球员身价、合同条款、地理迁移等大量复杂信息。然而，目前行业内的转会数据管理仍面临明显的痛点。

一方面，公开数据来源高度分散。Transfermarkt、FIFA官网、各联赛官方平台等渠道各自维护独立数据，格式不统一，球员姓名拼写、俱乐部归属、联赛层级等基础信息存在大量不一致，从业人员（球探、经纪人、数据分析师）需要耗费大量时间进行人工比对和清洗，严重影响工作效率。

另一方面，现有平台以公开展示为主，缺乏面向从业人员的专业管理功能。球探和经纪人无法在同一系统内完成数据录入、历史转会追踪、球员身价趋势分析等操作，往往依赖Excel表格或私有笔记进行管理，既不规范也难以共享协作。更值得关注的是，转会数据具有明显的时空属性——转会发生的时间、转出地与转入地的地理位置、所属联赛层级等维度，对于分析转会规律、识别市场机会具有重要价值，但现有工具对这些维度的整合与查询支持十分有限。

基于以上现实问题，本项目拟设计并实现一个面向足球行业从业人员的转会数据管理与分析平台，通过规范化的数据库设计，整合球员、俱乐部、教练、联赛、转会记录等多维度信息，支持从业人员高效录入、查询与分析转会数据，同时为管理员提供统一的数据维护入口，保障数据的准确性与时效性。

\subsection{选题意义}

考虑到足球转会市场中数据分散、查询低效与管理不规范等问题，本项目设计一套面向足球行业从业人员的转会数据管理与分析平台，主要服务于普通从业用户与平台管理员两类群体。

普通用户（包括球探、经纪人、数据分析师等）可通过平台按球员位置、国籍、年龄、FIFA评分、转会费区间、联赛归属、地理区域等多维度条件组合筛选转会记录，有效解决现有工具中"条件单一、无法组合查询"的痛点；同时可查看球员历史转会轨迹、俱乐部转入转出统计等聚合信息，为转会谈判与球员评估提供数据支撑。平台管理员能够通过统一入口对球员、俱乐部、教练、转会记录及各类标准对照表进行增删改查，保证数据的规范性与一致性，避免多源数据带来的冗余与冲突。

从行业角度来看，规范化的数据库设计将分散的转会信息整合为可查询、可分析的结构化资产，为转会市场的量化研究提供数据基础，有助于推动足球行业数据化管理水平的整体提升。

\subsection{范围界定}

本平台是一个面向足球行业从业人员的转会数据管理系统，旨在整合球员、俱乐部、教练、联赛等多维度数据，支持转会记录的规范化录入与多条件筛选分析。

\textbf{用户：}
\begin{itemize}[leftmargin=2em]
    \item 足球行业从业人员（球探、经纪人、数据分析师等）：普通用户，具备数据查询与筛选权限
    \item 平台管理员：具备全部数据的增删改查权限，负责维护数据准确性与完整性
\end{itemize}

\textbf{功能：}
\begin{itemize}[leftmargin=2em]
    \item 管理员可对球员、俱乐部、教练、转会记录等核心数据进行增删改查，并维护国家、联赛、位置、球员类型等标准对照表
    \item 普通用户可按球员姓名、位置、国籍、年龄、FIFA综合评分等条件查询球员信息，并查看球员历史转会记录
    \item 普通用户可按俱乐部名称、所属国家、所属联赛等条件查询俱乐部信息，查看俱乐部转入转出历史统计
    \item 普通用户可按转会费区间、转会时间段、转出/转入联赛、球员类型、地理区域等多维度条件组合筛选转会记录
    \item 系统自动关联球员身价、转会费、地理坐标、转会周次等事实信息，支持转会趋势的统计分析
\end{itemize}

% ============================================================
\section{第二阶段：需求分析}
% ============================================================

\subsection{需求分析的过程描述}

\subsubsection{用户访谈}

小组成员通过对足球行业从业人员的访谈，以及对现有转会数据平台的调研，梳理了当前转会数据管理中的核心痛点。

受访球探A表示，日常工作中需要频繁查阅球员的历史转会记录，了解其在不同联赛、不同俱乐部的流动轨迹，以判断球员的市场价值走势。目前他主要依赖Transfermarkt网站，但该网站以展示为主，无法自定义筛选条件组合，也无法导出结构化数据供进一步分析，每次查询都需要手动翻查多个页面，效率极低。

受访经纪人B表示，在谈判转会费时，需要快速检索同位置、同年龄段球员的历史成交价格作为参考依据。现有工具缺乏按位置、年龄、转会费区间组合查询的功能，往往需要依赖个人积累的Excel表格，数据更新不及时，且难以与同事共享协作。

受访数据分析师C表示，其所在机构希望分析不同联赛之间的转会流向规律，例如哪些联赛是主要的球员输出方，哪些是主要的引进方，以及转会的地理分布特征。但目前公开数据缺乏标准化的地理坐标和联赛层级信息，难以直接用于空间分析，数据清洗工作占据了大量时间。

\subsubsection{竞品分析}

Transfermarkt是目前最主流的转会数据平台，信息全面，但以公开展示为主，缺乏面向从业人员的数据管理与自定义分析功能，且数据格式不适合直接导入数据库使用，无法支持复杂条件的组合查询。

FIFA官方数据库数据权威，但访问受限，普通从业人员无法直接使用，且不提供历史转会的地理信息，对于需要分析转会地理流向的用户而言存在明显缺口。

综合以上调研，本平台的核心需求定位为：为从业人员提供结构化、可多维筛选的转会数据查询环境，同时为管理员提供规范的数据维护入口，实现数据的统一管理与高效利用。

\subsection{组织机构情况与用户分类}

\subsubsection{组织机构情况}

\begin{longtable}{>{\centering\arraybackslash}p{1cm} >{\centering\arraybackslash}p{3cm} p{5cm} p{5cm}}
\toprule
\textbf{序号} & \textbf{用户角色} & \textbf{描述} & \textbf{功能} \\
\midrule
\endfirsthead
\toprule
\textbf{序号} & \textbf{用户角色} & \textbf{描述} & \textbf{功能} \\
\midrule
\endhead
1 & 普通用户（从业人员） & 球探、经纪人、数据分析师等，使用系统进行数据查询与筛选分析 & 查询球员、俱乐部、转会记录；多维筛选与统计 \\
\midrule
2 & 管理员 & 负责平台数据的录入与维护，保证数据准确性与时效性 & 增删改查所有核心表与对照表 \\
\bottomrule
\end{longtable}

\subsubsection{用户分类}

\begin{longtable}{>{\centering\arraybackslash}p{1cm} >{\centering\arraybackslash}p{2.5cm} >{\centering\arraybackslash}p{3cm} p{6.5cm}}
\toprule
\textbf{序号} & \textbf{用户角色} & \textbf{分类名称} & \textbf{具体功能} \\
\midrule
\endfirsthead
\toprule
\textbf{序号} & \textbf{用户角色} & \textbf{分类名称} & \textbf{具体功能} \\
\midrule
\endhead
1 & 普通用户 & 球员信息查询 & 按姓名、位置、国籍、年龄、FIFA评分等条件查询球员 \\
\midrule
2 & 普通用户 & 俱乐部信息查询 & 按名称、国家、联赛等条件查询俱乐部及其转入转出统计 \\
\midrule
3 & 普通用户 & 转会记录筛选 & 按转会费、时间、联赛、地区、球员类型等多维条件组合筛选 \\
\midrule
4 & 管理员 & 核心数据维护 & 对球员、俱乐部、教练、转会记录进行增删改查 \\
\midrule
5 & 管理员 & 对照表维护 & 维护国家、联赛、位置、球员类型等标准对照表 \\
\bottomrule
\end{longtable}

\subsection{数据流图（DFD）}

\subsubsection{第一层数据流图}

系统包含以下五个主要处理过程：对照表管理、球员信息管理、俱乐部与教练信息管理、转会记录管理、数据查询与筛选。外部实体为管理员与普通用户（从业人员）。

主要数据流向如下：管理员向对照表管理过程提交国家、联赛、位置、球员类型等标准项，存入对应对照表；管理员向球员信息管理过程提交球员数据，存入球员维表；管理员向俱乐部与教练信息管理过程提交相关数据，存入俱乐部与教练维表；管理员向转会记录管理过程提交转会事实数据，存入转会事实表；普通用户向数据查询与筛选过程提交查询条件，系统跨多表联查后返回结果集。

\subsubsection{第二层数据流图}

\textbf{1\quad 对照表管理}

\begin{longtable}{p{4cm} p{4.5cm} p{4.5cm}}
\toprule
\textbf{子过程} & \textbf{输入} & \textbf{输出} \\
\midrule
\endfirsthead
\toprule
\textbf{子过程} & \textbf{输入} & \textbf{输出} \\
\midrule
\endhead
国家对照表维护 & 管理员录入国家信息 & country\_dim \\
联赛对照表维护 & 管理员录入联赛信息 & league\_dim \\
位置对照表维护 & 管理员录入位置信息 & position\_dim \\
球员类型对照表维护 & 管理员录入类型信息 & player\_type\_dim \\
\bottomrule
\end{longtable}

\textbf{2\quad 球员信息管理}

\begin{longtable}{p{4cm} p{4.5cm} p{4.5cm}}
\toprule
\textbf{子过程} & \textbf{输入} & \textbf{输出} \\
\midrule
\endfirsthead
\toprule
\textbf{子过程} & \textbf{输入} & \textbf{输出} \\
\midrule
\endhead
球员信息录入/更新 & 管理员提交球员数据 & players \\
球员信息删除 & 管理员操作指令 & players更新 \\
球员信息查询 & 普通用户查询条件 & 球员信息结果集 \\
\bottomrule
\end{longtable}

\textbf{3\quad 俱乐部与教练信息管理}

\begin{longtable}{p{4cm} p{4.5cm} p{4.5cm}}
\toprule
\textbf{子过程} & \textbf{输入} & \textbf{输出} \\
\midrule
\endfirsthead
\toprule
\textbf{子过程} & \textbf{输入} & \textbf{输出} \\
\midrule
\endhead
教练信息维护 & 管理员提交教练数据 & coaches \\
俱乐部信息维护 & 管理员提交俱乐部数据 & clubs \\
俱乐部查询 & 普通用户查询条件 & 俱乐部信息结果集 \\
\bottomrule
\end{longtable}

\textbf{4\quad 转会记录管理}

\begin{longtable}{p{4cm} p{4.5cm} p{4.5cm}}
\toprule
\textbf{子过程} & \textbf{输入} & \textbf{输出} \\
\midrule
\endfirsthead
\toprule
\textbf{子过程} & \textbf{输入} & \textbf{输出} \\
\midrule
\endhead
转会记录录入/更新 & 管理员提交转会事实数据 & transfers \\
转会记录删除 & 管理员操作指令 & transfers更新 \\
转会记录多维筛选 & 普通用户筛选条件 & 转会记录结果集 \\
\bottomrule
\end{longtable}

\subsection{数据字典}

\subsubsection{数据项}

\textbf{（一）国家维表 country\_dim}

\begin{longtable}{p{4cm} p{2.5cm} p{1.5cm} p{2cm} p{3cm}}
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endfirsthead
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endhead
country\_dim\_id & INT & PK & NOT NULL & 国家唯一标识 \\
country\_name & VARCHAR(100) & & NOT NULL & 国家名称 \\
country\_name\_normalized & VARCHAR(100) & & NOT NULL & 标准化国家名称 \\
\bottomrule
\end{longtable}

\textbf{（二）联赛维表 league\_dim}

\begin{longtable}{p{4cm} p{2.5cm} p{1.5cm} p{2cm} p{3cm}}
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endfirsthead
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endhead
league\_dim\_id & INT & PK & NOT NULL & 联赛唯一标识 \\
league\_name & VARCHAR(100) & & NOT NULL & 联赛名称 \\
league\_name\_normalized & VARCHAR(100) & & NOT NULL & 标准化联赛名称 \\
country\_dim\_id & INT & FK & NOT NULL & 所属国家，引用 country\_dim \\
\bottomrule
\end{longtable}

\textbf{（三）位置维表 position\_dim}

\begin{longtable}{p{4cm} p{2.5cm} p{1.5cm} p{2cm} p{3cm}}
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endfirsthead
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endhead
position\_dim\_id & INT & PK & NOT NULL & 位置唯一标识 \\
position\_name & VARCHAR(50) & & NOT NULL & 位置名称（如中场、前锋） \\
position\_name\_normalized & VARCHAR(50) & & NOT NULL & 标准化位置名称 \\
\bottomrule
\end{longtable}

\textbf{（四）球员类型维表 player\_type\_dim}

\begin{longtable}{p{4cm} p{2.5cm} p{1.5cm} p{2cm} p{3cm}}
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endfirsthead
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endhead
player\_type\_dim\_id & INT & PK & NOT NULL & 球员类型唯一标识 \\
player\_type & VARCHAR(50) & & NOT NULL & 类型名称（如 Defender、Forward） \\
player\_type\_normalized & VARCHAR(50) & & NOT NULL & 标准化类型名称 \\
\bottomrule
\end{longtable}

\textbf{（五）教练维表 coaches}

\begin{longtable}{p{4.5cm} p{2.5cm} p{1cm} p{2cm} p{3cm}}
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endfirsthead
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endhead
coach\_id & INT & PK & NOT NULL & 教练唯一标识 \\
coach\_url & VARCHAR(200) & & NULL & 教练主页链接 \\
short\_name & VARCHAR(50) & & NOT NULL & 教练简称 \\
long\_name & VARCHAR(100) & & NOT NULL & 教练全名 \\
dob & DATE & & NULL & 出生日期 \\
nationality\_country\_dim\_id & INT & FK & NULL & 国籍，引用 country\_dim \\
nationality\_id & INT & & NULL & 国籍原始编号 \\
face\_url & VARCHAR(200) & & NULL & 头像链接 \\
\bottomrule
\end{longtable}

\textbf{（六）球员维表 players}

\begin{longtable}{p{4.5cm} p{2.5cm} p{1cm} p{2cm} p{3cm}}
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endfirsthead
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endhead
player\_key & INT & PK & NOT NULL & 球员唯一标识 \\
player\_name & VARCHAR(100) & & NOT NULL & 球员姓名 \\
player\_name\_normalized & VARCHAR(100) & & NOT NULL & 标准化姓名 \\
position\_dim\_id & INT & FK & NULL & 场上位置，引用 position\_dim \\
age & INT & & NULL & 年龄 \\
transfer\_record\_count & INT & & NULL & 历史转会次数 \\
first\_transfer\_date & DATE & & NULL & 首次转会日期 \\
last\_transfer\_date & DATE & & NULL & 最近转会日期 \\
player\_match\_status & VARCHAR(20) & & NULL & 与FIFA数据匹配状态 \\
player\_name\_match\_key & VARCHAR(100) & & NULL & 匹配用标准化键 \\
player\_id & INT & & NULL & FIFA球员编号 \\
fifa\_version & VARCHAR(20) & & NULL & FIFA版本 \\
fifa\_update & VARCHAR(20) & & NULL & FIFA更新版本 \\
short\_name & VARCHAR(50) & & NULL & FIFA简称 \\
long\_name & VARCHAR(100) & & NULL & FIFA全名 \\
overall & INT & & NULL & FIFA综合评分（0--99） \\
potential & INT & & NULL & FIFA潜力评分（0--99） \\
team\_id & INT & & NULL & 当前所属球队ID \\
team\_name & VARCHAR(100) & & NULL & 当前所属球队名称 \\
team\_country\_dim\_id & INT & FK & NULL & 球队所属国家，引用 country\_dim \\
team\_league\_dim\_id & INT & FK & NULL & 球队所属联赛，引用 league\_dim \\
nationality\_country\_dim\_id & INT & FK & NULL & 球员国籍，引用 country\_dim \\
fifa\_update\_date & DATE & & NULL & FIFA数据更新日期 \\
player\_source\_table & VARCHAR(50) & & NULL & 数据来源表标识 \\
\bottomrule
\end{longtable}

\textbf{（七）俱乐部维表 clubs}

\begin{longtable}{p{4.5cm} p{2.5cm} p{1cm} p{2cm} p{3cm}}
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endfirsthead
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endhead
club\_key & INT & PK & NOT NULL & 俱乐部唯一标识 \\
club\_name & VARCHAR(100) & & NOT NULL & 俱乐部名称 \\
club\_name\_normalized & VARCHAR(100) & & NOT NULL & 标准化名称 \\
country\_dim\_id & INT & FK & NULL & 所属国家，引用 country\_dim \\
league\_dim\_id & INT & FK & NULL & 所属联赛，引用 league\_dim \\
origin\_transfer\_count & INT & & NULL & 历史转出次数 \\
destination\_transfer\_count & INT & & NULL & 历史转入次数 \\
team\_match\_status & VARCHAR(20) & & NULL & 与FIFA数据匹配状态 \\
team\_id & INT & & NULL & FIFA球队编号 \\
fifa\_version & VARCHAR(20) & & NULL & FIFA版本 \\
fifa\_update & VARCHAR(20) & & NULL & FIFA更新版本 \\
team\_name & VARCHAR(100) & & NULL & FIFA球队名称 \\
coach\_id & INT & FK & NULL & 现任主教练，引用 coaches \\
team\_overall & INT & & NULL & FIFA球队综合评分 \\
fifa\_update\_date & DATE & & NULL & FIFA数据更新日期 \\
\bottomrule
\end{longtable}

\textbf{（八）转会事实表 transfers}

\begin{longtable}{p{4.5cm} p{2.8cm} p{1cm} p{2cm} p{3cm}}
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endfirsthead
\toprule
\textbf{字段名} & \textbf{类型} & \textbf{键} & \textbf{约束} & \textbf{说明} \\
\midrule
\endhead
transfer\_id & INT & PK & NOT NULL & 转会记录唯一标识 \\
player\_key & INT & FK & NOT NULL & 转会球员，引用 players \\
origin\_club\_key & INT & FK & NULL & 转出俱乐部，引用 clubs \\
destination\_club\_key & INT & FK & NULL & 转入俱乐部，引用 clubs \\
position\_dim\_id & INT & FK & NULL & 转会时球员位置，引用 position\_dim \\
age & INT & & NULL & 转会时年龄 \\
player\_market\_value & DECIMAL(15,2) & & NULL & 球员市场身价（欧元） \\
cost & DECIMAL(15,2) & & NULL & 实际转会费（欧元） \\
date\_of\_transfer & DATE & & NULL & 转会日期 \\
destination\_latitude & DECIMAL(9,6) & & NULL & 转入地纬度 \\
destination\_longitude & DECIMAL(9,6) & & NULL & 转入地经度 \\
destination\_region & VARCHAR(100) & & NULL & 转入地区域名称 \\
origin\_latitude & DECIMAL(9,6) & & NULL & 转出地纬度 \\
origin\_longitude & DECIMAL(9,6) & & NULL & 转出地经度 \\
origin\_region & VARCHAR(100) & & NULL & 转出地区域名称 \\
week\_of\_transfer & INT & & NULL & 转会所在年内周次 \\
player\_type\_dim\_id & INT & FK & NULL & 球员类型，引用 player\_type\_dim \\
\bottomrule
\end{longtable}

\subsubsection{数据结构}

\begin{longtable}{>{\centering\arraybackslash}p{0.8cm} p{3cm} p{4cm} p{6cm}}
\toprule
\textbf{编号} & \textbf{数据结构名} & \textbf{含义说明} & \textbf{组成} \\
\midrule
\endfirsthead
\toprule
\textbf{编号} & \textbf{数据结构名} & \textbf{含义说明} & \textbf{组成} \\
\midrule
\endhead
1 & 国家对照信息 & 标准国家名称清单 & country\_dim\_id, country\_name, country\_name\_normalized \\
\midrule
2 & 联赛对照信息 & 标准联赛名称清单，含所属国家 & league\_dim\_id, league\_name, league\_name\_normalized, country\_dim\_id \\
\midrule
3 & 位置对照信息 & 球员场上位置标准清单 & position\_dim\_id, position\_name, position\_name\_normalized \\
\midrule
4 & 球员类型对照信息 & 转会球员类型标准清单 & player\_type\_dim\_id, player\_type, player\_type\_normalized \\
\midrule
5 & 教练信息 & 教练基础身份与国籍信息 & coach\_id, short\_name, long\_name, dob, nationality\_country\_dim\_id, nationality\_id, coach\_url, face\_url \\
\midrule
6 & 球员信息 & 球员基础属性、FIFA评分及转会统计 & player\_key, player\_name, position\_dim\_id, age, transfer\_record\_count, first\_transfer\_date, last\_transfer\_date, overall, potential, team\_country\_dim\_id, team\_league\_dim\_id, nationality\_country\_dim\_id \\
\midrule
7 & 俱乐部信息 & 俱乐部基础属性、联赛归属及转会统计 & club\_key, club\_name, country\_dim\_id, league\_dim\_id, origin\_transfer\_count, destination\_transfer\_count, coach\_id, team\_overall \\
\midrule
8 & 转会记录 & 单次转会事件的完整事实信息 & transfer\_id, player\_key, origin\_club\_key, destination\_club\_key, position\_dim\_id, age, player\_market\_value, cost, date\_of\_transfer, origin\_region, destination\_region, origin\_latitude, origin\_longitude, destination\_latitude, destination\_longitude, week\_of\_transfer, player\_type\_dim\_id \\
\bottomrule
\end{longtable}

\subsubsection{数据流}

\textbf{第一层数据流}

\begin{longtable}{>{\centering\arraybackslash}p{0.8cm} p{2.5cm} p{3cm} p{1.5cm} p{1.5cm} p{3.5cm}}
\toprule
\textbf{编号} & \textbf{数据流名} & \textbf{说明} & \textbf{来源} & \textbf{去向} & \textbf{组成} \\
\midrule
\endfirsthead
\toprule
\textbf{编号} & \textbf{数据流名} & \textbf{说明} & \textbf{来源} & \textbf{去向} & \textbf{组成} \\
\midrule
\endhead
1 & 对照表录入 & 管理员维护国家/联赛/位置/类型标准项 & 管理员 & 对照表管理 & country\_dim / league\_dim / position\_dim / player\_type\_dim \\
\midrule
2 & 对照表数据 & 存储后的标准对照信息 & 对照表管理 & 对照表存储 & 同上 \\
\midrule
3 & 球员信息录入 & 管理员提交球员数据 & 管理员 & 球员信息管理 & player\_key, player\_name, position\_dim\_id, age, overall, potential, nationality\_country\_dim\_id 等 \\
\midrule
4 & 球员数据 & 存储后的球员信息 & 球员信息管理 & players & 球员信息全字段 \\
\midrule
5 & 俱乐部/教练录入 & 管理员提交俱乐部与教练数据 & 管理员 & 俱乐部与教练信息管理 & club\_key, club\_name, country\_dim\_id, league\_dim\_id, coach\_id 等 \\
\midrule
6 & 俱乐部/教练数据 & 存储后的俱乐部与教练信息 & 俱乐部与教练信息管理 & clubs / coaches & 俱乐部/教练信息全字段 \\
\midrule
7 & 转会记录录入 & 管理员提交转会事实数据 & 管理员 & 转会记录管理 & transfer\_id, player\_key, origin\_club\_key, destination\_club\_key, cost, date\_of\_transfer 等 \\
\midrule
8 & 转会数据 & 存储后的转会记录 & 转会记录管理 & transfers & 转会记录全字段 \\
\midrule
9 & 查询条件 & 普通用户提交的筛选参数 & 普通用户 & 数据查询与筛选 & 位置、国籍、转会费区间、时间段、联赛、地区等 \\
\midrule
10 & 查询结果 & 系统返回的匹配记录 & 数据查询与筛选 & 普通用户 & 球员信息、俱乐部信息、转会记录 \\
\bottomrule
\end{longtable}

\textbf{第二层数据流}

\begin{longtable}{>{\centering\arraybackslash}p{0.8cm} p{2.5cm} p{3cm} p{1.5cm} p{1.5cm} p{3.5cm}}
\toprule
\textbf{编号} & \textbf{数据流名} & \textbf{说明} & \textbf{来源} & \textbf{去向} & \textbf{组成} \\
\midrule
\endfirsthead
\toprule
\textbf{编号} & \textbf{数据流名} & \textbf{说明} & \textbf{来源} & \textbf{去向} & \textbf{组成} \\
\midrule
\endhead
11 & 国家信息录入 & 新增或更新国家标准项 & 管理员 & 国家对照表维护 & country\_dim\_id, country\_name, country\_name\_normalized \\
\midrule
12 & 联赛信息录入 & 新增或更新联赛标准项 & 管理员 & 联赛对照表维护 & league\_dim\_id, league\_name, country\_dim\_id \\
\midrule
13 & 球员基础信息 & 球员身份与评分数据 & 管理员 & 球员信息录入/更新 & player\_key, player\_name, age, overall, potential \\
\midrule
14 & 球员外键关联 & 位置、国籍、联赛等关联编号 & 对照表存储 & 球员信息录入/更新 & position\_dim\_id, nationality\_country\_dim\_id, team\_league\_dim\_id \\
\midrule
15 & 教练基础信息 & 教练身份与国籍数据 & 管理员 & 教练信息维护 & coach\_id, short\_name, long\_name, dob, nationality\_country\_dim\_id \\
\midrule
16 & 俱乐部基础信息 & 俱乐部名称、归属与统计数据 & 管理员 & 俱乐部信息维护 & club\_key, club\_name, country\_dim\_id, league\_dim\_id, coach\_id \\
\midrule
17 & 转会事实数据 & 单次转会的完整事实字段 & 管理员 & 转会记录录入/更新 & transfer\_id, player\_key, origin\_club\_key, destination\_club\_key, cost, date\_of\_transfer, 地理坐标, week\_of\_transfer \\
\midrule
18 & 球员查询条件 & 按姓名/位置/国籍/年龄筛选 & 普通用户 & 球员信息查询 & player\_name, position\_dim\_id, nationality\_country\_dim\_id, age范围 \\
\midrule
19 & 球员查询结果 & 匹配的球员记录集 & 球员信息查询 & 普通用户 & players join position\_dim, country\_dim \\
\midrule
20 & 转会筛选条件 & 多维度转会记录筛选参数 & 普通用户 & 转会记录多维筛选 & cost范围, date\_of\_transfer范围, origin\_region, destination\_region, player\_type\_dim\_id \\
\midrule
21 & 转会筛选结果 & 匹配的转会记录集 & 转会记录多维筛选 & 普通用户 & transfers join players, clubs, position\_dim, player\_type\_dim \\
\bottomrule
\end{longtable}

\subsubsection{数据存储}

\begin{longtable}{>{\centering\arraybackslash}p{0.8cm} p{3cm} p{3.5cm} p{3cm} p{3cm}}
\toprule
\textbf{编号} & \textbf{数据存储名} & \textbf{说明} & \textbf{输入数据流} & \textbf{输出数据流} \\
\midrule
\endfirsthead
\toprule
\textbf{编号} & \textbf{数据存储名} & \textbf{说明} & \textbf{输入数据流} & \textbf{输出数据流} \\
\midrule
\endhead
1 & country\_dim & 国家标准对照表 & 国家信息录入 & 联赛/球员/俱乐部/教练外键引用 \\
\midrule
2 & league\_dim & 联赛标准对照表 & 联赛信息录入 & 球员/俱乐部外键引用 \\
\midrule
3 & position\_dim & 位置标准对照表 & 位置信息录入 & 球员/转会记录外键引用 \\
\midrule
4 & player\_type\_dim & 球员类型对照表 & 类型信息录入 & 转会记录外键引用 \\
\midrule
5 & coaches & 教练维表 & 教练信息维护 & 俱乐部外键引用、教练查询 \\
\midrule
6 & players & 球员维表 & 球员信息录入/更新 & 转会记录外键引用、球员查询 \\
\midrule
7 & clubs & 俱乐部维表 & 俱乐部信息维护 & 转会记录外键引用、俱乐部查询 \\
\midrule
8 & transfers & 转会事实表 & 转会记录录入/更新 & 转会记录多维筛选查询 \\
\bottomrule
\end{longtable}

\end{document}

