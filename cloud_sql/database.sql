PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE organization (
	id VARCHAR(75) NOT NULL, 
	users TEXT, 
	products TEXT, 
	tokens TEXT, 
	kinds TEXT, 
	name VARCHAR(120), 
	original_name VARCHAR(120), 
	created_time DATETIME, 
	last_updated_time DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	UNIQUE (original_name)
);
INSERT INTO organization VALUES('993a39cdeed84d72851efe581b9a74ed','["jslee@narantech.com"]','["mibp", "mibs", "mibio"]','{"access": "d45eb188dd4511251ae7073a447050ad"}','{}','naran','Naran','2018-08-14 05:01:15.430400','2018-08-14 05:02:16.091136');
INSERT INTO organization VALUES('a93e9136d02b69cacc1fb15851105009','["nmkim+console0816@narantech.com"]','[]','{"access": "342c4f72253f466f50916cb67270e4d4"}','{}','테스트 그룹','테스트 그룹','2018-08-16 02:30:46.822859',NULL);
CREATE TABLE invite (
	id VARCHAR(75) NOT NULL, 
	email VARCHAR(75), 
	organization_id VARCHAR(75), 
	product_id VARCHAR(75), 
	`key` VARCHAR(75), 
	level INTEGER, 
	invited_time DATETIME, 
	invited_user VARCHAR(75), 
	accepted INTEGER, 
	accepted_time DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO invite VALUES('dadd656aa1f640d3a09c8eb21951e1bc','jwkwon@narantech.com','993a39cdeed84d72851efe581b9a74ed','','bf116cace6424ee0a6eb2532415fe728',1,'2018-08-14 06:06:46.649717','jslee@narantech.com',0,NULL);
INSERT INTO invite VALUES('25327cc712954155aba934cb4242a35c','kyong.jh@narantech.com','993a39cdeed84d72851efe581b9a74ed','','88860a8ffede4767a68df77af82ddaff',1,'2018-08-14 06:07:17.531441','jslee@narantech.com',1,'2018-08-14 09:03:43.233956');
INSERT INTO invite VALUES('9d035938696a48a0bb512a11a351456b','serim.jeon@narantech.com','993a39cdeed84d72851efe581b9a74ed','','9ac0ecf68e704baca9158c0177d67a77',1,'2018-08-14 06:07:29.921584','jslee@narantech.com',1,'2018-08-14 06:41:36.066678');
INSERT INTO invite VALUES('07fb16f0c45a46cbb26513d4f50d7bd8','hdkim@narantech.com','993a39cdeed84d72851efe581b9a74ed','','31f2bef05a3345bdb12bccd9561c04a5',1,'2018-08-14 06:07:43.421348','jslee@narantech.com',1,'2018-08-14 06:08:38.327129');
INSERT INTO invite VALUES('cf257abbf67741bb8eb07bc74dcb45a1','jongmin@narantech.com','993a39cdeed84d72851efe581b9a74ed','','b29013be32b544cca26101c6c8b03a0a',1,'2018-08-14 06:07:56.769778','jslee@narantech.com',1,'2018-08-14 06:08:07.132437');
INSERT INTO invite VALUES('95202be860aa4f828069ffd97f871ef4','nmkim@narantech.com','993a39cdeed84d72851efe581b9a74ed','','f5e33a14123e41d69a183acc51d12b10',1,'2018-08-14 06:08:08.700483','jslee@narantech.com',1,'2018-08-14 06:19:53.075108');
INSERT INTO invite VALUES('85954569e93549d6a3e1fe74d71d5d06','woojin@narantech.com','993a39cdeed84d72851efe581b9a74ed','','0c5cc037645c499092120a8c5ce36d24',1,'2018-08-14 06:08:19.282317','jslee@narantech.com',1,'2018-08-14 06:08:50.811648');
INSERT INTO invite VALUES('5f0f9413dc85462baa2d28c04c02e3f2','choikyle@narantech.com','993a39cdeed84d72851efe581b9a74ed','','9e8763396a4a40f497404e3997df33f3',1,'2018-08-14 06:08:29.384964','jslee@narantech.com',1,'2018-08-14 06:22:47.675541');
INSERT INTO invite VALUES('fb785b3ac8fd4b0583a0aaf255b0f769','lhtak@narantech.com','993a39cdeed84d72851efe581b9a74ed','','1a1afd644bf74c7fbda3d60d047c60b0',1,'2018-08-14 06:12:22.349404','jslee@narantech.com',1,'2018-08-14 06:12:47.577082');
CREATE TABLE user (
	id VARCHAR(75) NOT NULL, 
	email VARCHAR(75) NOT NULL, 
	name VARCHAR(75), 
	firebase_user_id VARCHAR(75), 
	email_verified BOOLEAN NOT NULL, 
	sign_in_provider VARCHAR(75), 
	photo_url VARCHAR(225), 
	created_time DATETIME, 
	last_access_time DATETIME, 
	ip_address VARCHAR(75), 
	level INTEGER, 
	organization_id VARCHAR(75), 
	PRIMARY KEY (id), 
	UNIQUE (email), 
	UNIQUE (firebase_user_id), 
	CHECK (email_verified IN (0, 1)), 
	FOREIGN KEY(organization_id) REFERENCES organization (id)
);
INSERT INTO user VALUES('XtxGnNysQXSg0zzDgJJpD1BRR172','jslee@narantech.com','Jaeseung Lee','XtxGnNysQXSg0zzDgJJpD1BRR172',1,'google.com','https://lh6.googleusercontent.com/-PSY5qMeC5vk/AAAAAAAAAAI/AAAAAAAAAAA/AB6qoq1vsG8shcIE6VuINH_SEVmU0eJTrg/mo/photo.jpg','2018-08-15 07:58:55.553358','2018-08-16 04:20:09.408539','127.0.0.1',0,'993a39cdeed84d72851efe581b9a74ed');
INSERT INTO user VALUES('2BhbjSpE0dVGjR6ahHBEN84IiBj2','jongmin@narantech.com','Jongmin Jeon','2BhbjSpE0dVGjR6ahHBEN84IiBj2',1,'google.com','https://lh4.googleusercontent.com/-UVkjFBgYm5Q/AAAAAAAAAAI/AAAAAAAAAAA/AAnnY7oLfMmTVhtM89zuTQg43Vet4amIgw/mo/photo.jpg','2018-08-14 06:08:21.724461','2018-08-14 06:30:42.972542','222.101.99.147',NULL,'993a39cdeed84d72851efe581b9a74ed');
INSERT INTO user VALUES('qya97luRq8aeewiil5AI1HDvsAl2','hdkim@narantech.com','Hyodong Kim','qya97luRq8aeewiil5AI1HDvsAl2',1,'google.com','https://lh5.googleusercontent.com/-ng_KFd-lgMA/AAAAAAAAAAI/AAAAAAAAAAA/AAnnY7qCHL1EHwckNthNP2tBs66ObbsCJw/mo/photo.jpg','2018-08-14 06:08:57.155722','2018-08-14 06:08:57.572618','222.101.99.147',NULL,'993a39cdeed84d72851efe581b9a74ed');
INSERT INTO user VALUES('LksVMuismXRxRHZ09B6dak1e0E52','woojin@narantech.com','Woojin Jung','LksVMuismXRxRHZ09B6dak1e0E52',1,'google.com','https://lh4.googleusercontent.com/-J5MUIIxLxSo/AAAAAAAAAAI/AAAAAAAACig/IPXyHKCmPgA/photo.jpg','2018-08-14 06:09:15.522297','2018-08-14 06:17:42.061452','222.101.99.147',NULL,'993a39cdeed84d72851efe581b9a74ed');
INSERT INTO user VALUES('DpunLaYiZwaGkBX9wspWFYWpZcj2','lhtak@narantech.com','Hyuntak Lee','DpunLaYiZwaGkBX9wspWFYWpZcj2',1,'google.com','https://lh6.googleusercontent.com/-kmhJd5oxqUE/AAAAAAAAAAI/AAAAAAAAAY4/8GjJE7nEjbA/photo.jpg','2018-08-14 06:12:59.815536','2018-08-14 06:13:00.430810','222.101.99.147',NULL,'993a39cdeed84d72851efe581b9a74ed');
INSERT INTO user VALUES('XUH0rGdmBAULT7lAAcTQdzExllf2','choikyle@narantech.com','Kyle Choi','XUH0rGdmBAULT7lAAcTQdzExllf2',1,'google.com','https://lh5.googleusercontent.com/-2Md7il5r9E0/AAAAAAAAAAI/AAAAAAAAABQ/pClVMXIv4Ug/photo.jpg','2018-08-14 06:23:03.021806','2018-08-14 09:08:26.108466','222.101.99.147',NULL,'993a39cdeed84d72851efe581b9a74ed');
INSERT INTO user VALUES('kkD7AapDajZOnWZsCcSsFcrWjvK2','serim.jeon@narantech.com','serim jeon','kkD7AapDajZOnWZsCcSsFcrWjvK2',0,'password','/static/images/user.png','2018-08-16 06:23:01.335765','2018-08-16 06:23:01.733181','127.0.0.1',NULL,'993a39cdeed84d72851efe581b9a74ed');
INSERT INTO user VALUES('2Dnx5yaoZ8due5bHE8zGvxWH9G53','kyong.jh@narantech.com','Jaehyun Kyong','2Dnx5yaoZ8due5bHE8zGvxWH9G53',1,'google.com','https://lh3.googleusercontent.com/-XFfmiKqHCDY/AAAAAAAAAAI/AAAAAAAAAAA/AAnnY7rlxO1s_BLZSCiWA8nCmQO8eDPM_g/mo/photo.jpg','2018-08-16 09:11:25.305724','2018-08-16 09:11:25.605695','127.0.0.1',NULL,'993a39cdeed84d72851efe581b9a74ed');
INSERT INTO user VALUES('t8N7pXts4LRT1lc2VsD7WBos2763','nmkim@narantech.com','Nammyeong Kim','t8N7pXts4LRT1lc2VsD7WBos2763',1,'google.com','https://lh4.googleusercontent.com/-2zg7MBjfmEM/AAAAAAAAAAI/AAAAAAAAAAA/AAnnY7pOMCp3pZs2WYE0DyaIVLzEEQKucQ/mo/photo.jpg','2018-08-16 00:47:37.402793','2018-08-16 02:29:33.002766','127.0.0.1',NULL,'993a39cdeed84d72851efe581b9a74ed');
INSERT INTO user VALUES('gjpRG9VmBeZNrq1huISeAKraLLO2','nmkim+console0816@narantech.com',NULL,'gjpRG9VmBeZNrq1huISeAKraLLO2',0,'password','/static/images/user.png','2018-08-16 02:30:12.327609','2018-08-16 02:39:12.091971','127.0.0.1',0,'a93e9136d02b69cacc1fb15851105009');
CREATE TABLE product (
	id VARCHAR(75) NOT NULL, 
	code VARCHAR(75), 
	developer_id VARCHAR(75), 
	`key` VARCHAR(75), 
	name VARCHAR(75), 
	created_time DATETIME, 
	last_updated_time DATETIME, 
	organization_id VARCHAR(75), 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organization (id)
);
INSERT INTO product VALUES('mibp','mibp','993a39cdeed84d72851efe581b9a74ed','cac9095c6a3e7764af27b51ca9ec41ee','MicroBot Push','2018-08-14 05:01:37.818735','2018-08-14 05:01:37.818756','993a39cdeed84d72851efe581b9a74ed');
INSERT INTO product VALUES('mibs','mibs','993a39cdeed84d72851efe581b9a74ed','b9a0d9f2b062bd1d52089f74eb194ae0','MicroBot Sense','2018-08-14 05:01:56.124537','2018-08-14 05:01:56.124539','993a39cdeed84d72851efe581b9a74ed');
INSERT INTO product VALUES('mibio','mibio','993a39cdeed84d72851efe581b9a74ed','df4f925b5233fc50b1a298e878d85367','MicroBot IO','2018-08-14 05:02:16.080140','2018-08-14 05:02:16.080143','993a39cdeed84d72851efe581b9a74ed');
INSERT INTO product VALUES('testmibA','testmibA','a93e9136d02b69cacc1fb15851105009','441c3eb099f4d1d6b468417f461cf898','test0816','2018-08-16 02:32:03.570196','2018-08-16 02:32:03.570199','a93e9136d02b69cacc1fb15851105009');
CREATE TABLE notikey (
	id INTEGER NOT NULL, 
	typ INTEGER, 
	name VARCHAR(75), 
	`key` VARCHAR(75), 
	is_dev INTEGER, 
	created_time DATETIME, 
	last_updated_time DATETIME, 
	last_updated_user VARCHAR(75), 
	organization_id VARCHAR(75), 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organization (id)
);
CREATE TABLE permission (
	id VARCHAR(75) NOT NULL, 
	permission VARCHAR(15), 
	user_id VARCHAR(75), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO permission VALUES('7d4a45d99a7e48c6b2cb4d6f24cba3d0','777','XtxGnNysQXSg0zzDgJJpD1BRR172');
INSERT INTO permission VALUES('5f16b6b7ed404f5981cf38d84f05bc92','777','2BhbjSpE0dVGjR6ahHBEN84IiBj2');
INSERT INTO permission VALUES('4c73787b998844cb8a07c6590db59dfe','777','qya97luRq8aeewiil5AI1HDvsAl2');
INSERT INTO permission VALUES('4f3a4b22ade544638b090c395e0d9b6c','777','LksVMuismXRxRHZ09B6dak1e0E52');
INSERT INTO permission VALUES('cbe03f31f3aa415abd65d904926e8a72','777','DpunLaYiZwaGkBX9wspWFYWpZcj2');
INSERT INTO permission VALUES('59717bcd13a340ed9b7d21a2ca143c37','777','XUH0rGdmBAULT7lAAcTQdzExllf2');
INSERT INTO permission VALUES('ea8dc258b67945feba679a055c583db8','777','kkD7AapDajZOnWZsCcSsFcrWjvK2');
INSERT INTO permission VALUES('32b7a2389cc0465ab5342b83e77f13ec','777','2Dnx5yaoZ8due5bHE8zGvxWH9G53');
INSERT INTO permission VALUES('99c02d33ed4949f79b8001d1309a32de','777','2Dnx5yaoZ8due5bHE8zGvxWH9G53');
INSERT INTO permission VALUES('3ec6e666bab94ecebe0404c7b8f6fcd7','777','XtxGnNysQXSg0zzDgJJpD1BRR172');
INSERT INTO permission VALUES('1937937aa52c4ce09626ea72c967be69','777','XtxGnNysQXSg0zzDgJJpD1BRR172');
INSERT INTO permission VALUES('922089b638014eb495b9333836fa5758','777','XtxGnNysQXSg0zzDgJJpD1BRR172');
INSERT INTO permission VALUES('27b1d3d75fb44654903609566e42c5ce','777','XtxGnNysQXSg0zzDgJJpD1BRR172');
INSERT INTO permission VALUES('237673e27d05489ebcae2eecd53c7fcb','777','XtxGnNysQXSg0zzDgJJpD1BRR172');
INSERT INTO permission VALUES('033b04e1cbf54f8cb45a5a21db9df9ea','777','t8N7pXts4LRT1lc2VsD7WBos2763');
INSERT INTO permission VALUES('7fb486c40a1f432483f720f70219e48d','777','gjpRG9VmBeZNrq1huISeAKraLLO2');
INSERT INTO permission VALUES('67024c6d30054daba16602c9e08ef567','777','kkD7AapDajZOnWZsCcSsFcrWjvK2');
INSERT INTO permission VALUES('ab00cc65a5964e4db3bc50bcce890860','777','2Dnx5yaoZ8due5bHE8zGvxWH9G53');
INSERT INTO permission VALUES('9650fc8530bd450fbeccc8880b6d5c13','777','2Dnx5yaoZ8due5bHE8zGvxWH9G53');
INSERT INTO permission VALUES('1efc3256732944b4ab30bce05a53e524','777','2Dnx5yaoZ8due5bHE8zGvxWH9G53');
CREATE TABLE product_stage (
	id VARCHAR(75) NOT NULL, 
	hook_url VARCHAR(120), 
	hook_client_key VARCHAR(120), 
	stage INTEGER, 
	created_time DATETIME, 
	last_updated_time DATETIME, 
	last_updated_user VARCHAR(75), 
	product_id VARCHAR(75), 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES product (id)
);
INSERT INTO product_stage VALUES('3c469dd63abe428585c9e74adea64f95','','',2,'2018-08-14 05:01:37.822549','2018-08-14 05:01:37.822551',NULL,'mibp');
INSERT INTO product_stage VALUES('04ca8219c5c64468a0e9e7f5c31ca655','','',2,'2018-08-14 05:01:56.127805','2018-08-14 05:01:56.127808',NULL,'mibs');
INSERT INTO product_stage VALUES('e8ddf0f4307b49c59535c945ac3d6ef5','','',2,'2018-08-14 05:02:16.083833','2018-08-14 05:02:16.083835',NULL,'mibio');
CREATE TABLE tester (
	id VARCHAR(75) NOT NULL, 
	email VARCHAR(75), 
	authorized BOOLEAN, 
	level INTEGER, 
	organization_id VARCHAR(75), 
	product_id VARCHAR(75), 
	PRIMARY KEY (id), 
	CHECK (authorized IN (0, 1)), 
	FOREIGN KEY(product_id) REFERENCES product (id)
);
CREATE TABLE model (
	id VARCHAR(75) NOT NULL, 
	code INTEGER, 
	name VARCHAR(75), 
	created_time DATETIME, 
	last_updated_time DATETIME, 
	last_updated_user VARCHAR(75), 
	product_stage_id VARCHAR(75), 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_stage_id) REFERENCES product_stage (id)
);
INSERT INTO model VALUES('e4542b7b93ce4622bdf947d7c2bac28f',0,'gen3','2018-08-14 11:45:34.595056','2018-08-14 11:45:34.595058','jslee@narantech.com','3c469dd63abe428585c9e74adea64f95');
INSERT INTO model VALUES('c935a58946244013b7babe19fbf24282',0,'v4','2018-08-14 11:46:16.410240','2018-08-14 11:46:16.410244','jslee@narantech.com','04ca8219c5c64468a0e9e7f5c31ca655');
INSERT INTO model VALUES('6ab095f89c6b4a969990ca22d0f8578b',0,'gen4','2018-08-16 06:23:32.645878','2018-08-16 06:23:32.645881','serim.jeon@narantech.com','e8ddf0f4307b49c59535c945ac3d6ef5');
INSERT INTO model VALUES('91d8fa56e18e4b758ca1a32d3d14fa55',2,'gen4','2018-08-16 06:24:06.163113','2018-08-16 06:24:06.163116','serim.jeon@narantech.com','3c469dd63abe428585c9e74adea64f95');
INSERT INTO model VALUES('3052ec6d6afc41dd8f4fd657a5c44b93',2,'example','2018-08-16 08:44:09.503384','2018-08-16 08:44:09.503387','kyong.jh@narantech.com','e8ddf0f4307b49c59535c945ac3d6ef5');
CREATE TABLE endpoint (
	id VARCHAR(75) NOT NULL, 
	version VARCHAR(75), 
	specifications TEXT, 
	created_time DATETIME, 
	last_updated_time DATETIME, 
	last_updated_user VARCHAR(75), 
	organization_id VARCHAR(75), 
	product_stage_id VARCHAR(75), 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_stage_id) REFERENCES product_stage (id)
);
INSERT INTO endpoint VALUES('5de6fd5bffae49bda964ae0942a2b1af','0.3',replace(replace('{\r\n    "product": "mibs",\r\n    "version": "0.3",\r\n    "requests": [{\r\n        "name": "get_measure",\r\n        "params": [],\r\n        "returns": [{\r\n            "name": "temperature",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "humidity",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "movement",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "illuminance",\r\n            "type": "uint16_t",\r\n            "length": 1\r\n        },{\r\n            "name": "noise",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "pressure",\r\n            "type": "uint32_t",\r\n            "length": 1\r\n        },{\r\n            "name": "usb_state",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "chemical_state",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "co2",\r\n            "type": "uint16_t",\r\n            "length": 1\r\n        },{\r\n            "name": "tvoc",\r\n            "type": "uint16_t",\r\n            "length": 1\r\n        }],\r\n        "timeout": 3\r\n    },\r\n    {\r\n        "name": "timer_setting",\r\n        "params": \r\n            [{\r\n                "name": "stalled_timer",\r\n                "type": "uint16_t",\r\n                "length": 1\r\n            },\r\n            {\r\n                "name": "moved_timer",\r\n                "type": "uint16_t",\r\n                "length": 1\r\n            }],\r\n        "returns": \r\n            [{\r\n                "name": "stalled_timer",\r\n                "type": "uint16_t",\r\n                "length": 1\r\n            },\r\n            {\r\n                "name": "moved_timer",\r\n                "type": "uint16_t",\r\n                "length": 1\r\n            }],\r\n        "timeout": 3\r\n    },\r\n    {\r\n        "name": "movement_sensitivity",\r\n        "params": \r\n            [{\r\n                "name": "value",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n        "returns": \r\n            [{\r\n                "name": "value",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n        "timeout": 3\r\n    },{\r\n        "name": "noise_setting",\r\n        "params": \r\n            [{\r\n                "name": "enable",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n        "returns": \r\n            [{\r\n                "name": "state",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n        "timeout": 3\r\n    },\r\n    {\r\n        "name": "chemical_setting",\r\n        "params": \r\n            [{\r\n                "name": "enable_type",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "sensing_mode",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n        "returns": \r\n            [{\r\n                "name": "state",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n        "timeout": 3\r\n    },\r\n    {\r\n        "name": "get_history",\r\n        "params": [],\r\n        "returns": \r\n            [{\r\n                "name": "total",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "index",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "temperature",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "humidity",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "pressure",\r\n                "type": "uint32_t",\r\n                "length": 1\r\n            },{\r\n                "name": "illuminance",\r\n                "type": "uint16_t",\r\n                "length": 1\r\n            },{\r\n                "name": "noise",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "movement",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "co2",\r\n                "type": "uint16_t",\r\n                "length": 1\r\n            },{\r\n                "name": "tvoc",\r\n                "type": "uint16_t",\r\n                "length": 1\r\n            }],\r\n        "dynamic_return": 1,\r\n        "timeout": 3\r\n    },\r\n    {\r\n        "name": "play_piezo",\r\n        "params": \r\n            [{\r\n                "name": "repeat_count",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "sound_number",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n        "returns": [],\r\n        "timeout": 3\r\n    },{\r\n        "name": "get_info",\r\n        "params": [],\r\n        "returns": [{\r\n                "name": "stalled_timer",\r\n                "type": "uint16_t",\r\n                "length": 1\r\n            },\r\n            {\r\n                "name": "moved_timer",\r\n                "type": "uint16_t",\r\n                "length": 1\r\n            },{\r\n                "name": "sensitivity",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "chemical_state",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "noise_state",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n        "timeout": 3\r\n    }],\r\n    "events":[{\r\n        "name": "touched",\r\n         "params":[{\r\n            "name": "temperature",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "humidity",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "movement",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "illuminance",\r\n            "type": "uint16_t",\r\n            "length": 1\r\n        },{\r\n            "name": "noise",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "pressure",\r\n            "type": "uint32_t",\r\n            "length": 1\r\n        },{\r\n            "name": "usb_state",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "chemical_state",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "co2",\r\n            "type": "uint16_t",\r\n            "length": 1\r\n        },{\r\n            "name": "tvoc",\r\n            "type": "uint16_t",\r\n            "length": 1\r\n        }]\r\n    },\r\n    {\r\n        "name":"movement",\r\n         "params": [{\r\n                "name": "data_t",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }]\r\n    },{\r\n        "name": "measured",\r\n         "params":[{\r\n            "name": "temperature",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "humidity",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "movement",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "illuminance",\r\n            "type": "uint16_t",\r\n            "length": 1\r\n        },{\r\n            "name": "noise",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "pressure",\r\n            "type": "uint32_t",\r\n            "length": 1\r\n        },{\r\n            "name": "usb_state",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "chemical_state",\r\n            "type": "uint8_t",\r\n            "length": 1\r\n        },{\r\n            "name": "co2",\r\n            "type": "uint16_t",\r\n            "length": 1\r\n        },{\r\n            "name": "tvoc",\r\n            "type": "uint16_t",\r\n            "length": 1\r\n        }]\r\n    }]\r\n}','\r',char(13)),'\n',char(10)),'2018-08-14 09:09:41.381801','2018-08-14 09:09:41.381803','kyong.jh@narantech.com','993a39cdeed84d72851efe581b9a74ed','04ca8219c5c64468a0e9e7f5c31ca655');
INSERT INTO endpoint VALUES('08fc51a9fe9b45e5ba598c128b0d594c','0.5',replace(replace('{\r\n    "product": "mibp",\r\n    "version": "0.5",\r\n    "requests": [{\r\n            "name": "push",\r\n            "params": [],\r\n            "returns": [],\r\n            "timeout": 10\r\n            },\r\n            {\r\n            "name": "release",\r\n            "params": [],\r\n            "returns": [],\r\n            "timeout": 10\r\n            },\r\n            {\r\n            "name": "press",\r\n            "params": [],\r\n            "returns": [{\r\n                "name": "duration",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n            "timeout": 10\r\n            },\r\n            {\r\n            "name": "set_mode",\r\n            "params": [{\r\n                "name": "mode",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n            "returns": [{\r\n                "name": "tip_state",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "calibration",\r\n                "type": "uint8_t",\r\n                "length" : 1\r\n            },{\r\n                "name":"duration",\r\n                "type":"uint8_t",\r\n                "length" : 1\r\n            },{\r\n                "name":"mode",\r\n                "type":"uint8_t",\r\n                "length" :1\r\n            }],\r\n            "timeout": 10\r\n            },\r\n            {\r\n            "name": "set_calibration",\r\n            "params": [{\r\n                "name": "calibration",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n            "returns": [{\r\n                "name": "calibration",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n            "timeout": 10\r\n            },\r\n            {\r\n            "name": "set_duration",\r\n            "params": [{\r\n                "name": "duration",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n            "returns": [{\r\n                "name": "duration",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n            "timeout": 10\r\n            },\r\n            {\r\n            "name": "set_timer",\r\n            "params": [{\r\n                "name": "current_week",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "currnet_hour",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "current_min",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "current_sec",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "id",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name":"repeat",\r\n                "type":"uint8_t",\r\n                "length":1\r\n            },{\r\n                "name":"hour",\r\n                "type":"uint8_t",\r\n                "length":1\r\n            },{\r\n                "name":"minite",\r\n                "type":"uint8_t",\r\n                "length":1\r\n            },{\r\n                "name":"enable",\r\n                "type":"uint8_t",\r\n                "length":1\r\n            },{\r\n                "name":"duration",\r\n                "type":"uint8_t",\r\n                "length":1\r\n            }],\r\n            "returns": [],\r\n            "timeout": 10\r\n            },\r\n            {\r\n            "name": "get_info",\r\n            "params": [],\r\n            "returns": [{\r\n                "name": "tip_state",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "calibration",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "duration",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },\r\n            {\r\n                "name": "onoff",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "mode",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n            "timeout": 10\r\n            },\r\n            {\r\n            "name": "set_onoff",\r\n            "params": [{\r\n                "name": "onoff",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n            "returns": [{\r\n                "name": "onoff",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            }],\r\n            "timeout": 10\r\n    }],\r\n    "events":[{\r\n        "name": "changed_state",\r\n        "params" : [{\r\n        		"name": "event_flag",\r\n        		"type": "uint8_t",\r\n        		"length": 1\r\n      		},{\r\n                "name": "touch_event",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n                "name": "tip_state",\r\n                "type": "uint8_t",\r\n                "length": 1\r\n            },{\r\n	            "name" : "onoff",\r\n	            "type" : "uint8_t",\r\n	            "length" : 1\r\n    	}]\r\n    }]\r\n}','\r',char(13)),'\n',char(10)),'2018-08-14 09:30:29.275321','2018-08-14 09:30:29.275322','serim.jeon@narantech.com','993a39cdeed84d72851efe581b9a74ed','3c469dd63abe428585c9e74adea64f95');
INSERT INTO endpoint VALUES('28bdb307595f45cdae0e2939e08fb123','0.1',replace(replace('{\r\n  "product": "mibio",\r\n  "version": "0.1",\r\n  "requests": [{\r\n      "name": "set_pin",\r\n      "params": [{\r\n        "name": "pin_number",\r\n        "type": "uint8_t",\r\n        "length": 1,\r\n        "default": 14\r\n      }],\r\n      "returns": [{\r\n        "name": "result",\r\n        "type": "uint8_t",\r\n        "length": 1\r\n      }],\r\n      "timeout": 3\r\n    },\r\n    {\r\n      "name": "clear_pin",\r\n      "params": [{\r\n        "name": "pin_number",\r\n        "type": "uint8_t",\r\n        "length": 1,\r\n        "default": 14\r\n      }],\r\n      "returns": [{\r\n        "name": "result",\r\n        "type": "uint8_t",\r\n        "length": 1\r\n      }],\r\n      "timeout": 3\r\n    }\r\n  ],\r\n  "events": [{\r\n    "name": "pin_interrupt",\r\n    "params": [{\r\n        "name": "pin_number",\r\n        "type": "uint8_t",\r\n        "length": 1\r\n      },\r\n      {\r\n        "name": "pin_state",\r\n        "type": "uint8_t",\r\n        "length": 1\r\n      }\r\n    ]\r\n  }]\r\n}','\r',char(13)),'\n',char(10)),'2018-08-16 09:18:43.526227','2018-08-16 09:18:43.526230','kyong.jh@narantech.com','993a39cdeed84d72851efe581b9a74ed','e8ddf0f4307b49c59535c945ac3d6ef5');
CREATE TABLE firmware (
	id VARCHAR(75) NOT NULL, 
	version VARCHAR(75), 
	path VARCHAR(225), 
	created_time DATETIME, 
	last_updated_time DATETIME, 
	last_updated_user VARCHAR(75), 
	model_id VARCHAR(75), 
	PRIMARY KEY (id), 
	FOREIGN KEY(model_id) REFERENCES model (id)
);
CREATE TABLE firmware_stage (
	id VARCHAR(75) NOT NULL, 
	version VARCHAR(75), 
	stage INTEGER, 
	before_stage INTEGER, 
	last_updated_time DATETIME, 
	firmware_id VARCHAR(75), 
	PRIMARY KEY (id), 
	FOREIGN KEY(firmware_id) REFERENCES firmware (id)
);
COMMIT;
