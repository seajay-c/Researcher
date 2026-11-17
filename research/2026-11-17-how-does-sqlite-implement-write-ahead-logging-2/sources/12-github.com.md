---
n: 12
url: https://github.com/sqlite/sqlite/blob/master/src/wal.c
title: Navigation Menu
fetched_at: 2026-11-17T07:02:15.615014Z
---

<!DOCTYPE html> 

[Skip to content](#start-of-content) 

## Navigation Menu

[Sign in](/login?return%5Fto=https%3A%2F%2Fgithub.com%2Fsqlite%2Fsqlite%2Fblob%2Fmaster%2Fsrc%2Fwal.c)

* Products

  * Platform
    * [![](https://github.githubassets.com/assets/platform-4ce65ae0bf273ce2.png)![](https://github.githubassets.com/assets/platform-dark-ac89fbf373737ed3.png)GitHubRepository hosting, code review, and collaboration](https://github.com/platform)
    * [![](https://github.githubassets.com/assets/copilot-e2b89335a66dba00.png)![](https://github.githubassets.com/assets/copilot-dark-2b28403b6080e898.png)CopilotAI coding agent for tasks, projects, and automated work](https://github.com/features/copilot)
  * Build & Ship
    * [ActionsCI/CD and automation](https://github.com/features/actions)
    * [Code QualityQuality analysis, fixes, and enforcement](https://github.com/features/code-quality)
    * [CodespacesCloud development environments](https://github.com/features/codespaces)
  * Secure
    * [Code SecurityVulnerability detection and remediation](https://github.com/security/advanced-security/code-security)
    * [Secret ProtectionSecret scanning and leak prevention](https://github.com/security/advanced-security/secret-protection)  
[All Features](https://github.com/features)
* Developers

  * Learn
    * [Documentation](https://docs.github.com/en)
    * [Training](https://learn.github.com/skills)
    * [Certifications](https://learn.github.com/credentials)
  * Build
    * [Build with Copilot](https://github.com/features/ai)
    * [Customize Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-copilot-overview)
    * [Integrations](https://github.com/marketplace)
  * Explore
    * [Trending repos](https://github.com/trending)
    * [GitHub Sponsors](https://github.com/open-source/sponsors)
    * [Developer articles](https://github.com/resources/articles)
  * Changelog
    * [![](https://github.githubassets.com/assets/changelog-fd687bff072883b0.png)![](https://github.githubassets.com/assets/changelog-dark-b1c25ae971bd641b.png)ChangelogYour source for the latest features, improvements, and fixes across GitHub products, all in one place.](https://github.blog/changelog/)
* Businesses

  * By Stage
    * [Enterprises](https://github.com/enterprise)
    * [Team](https://github.com/team)
    * [Startups](https://github.com/enterprise/startups)
    * [Nonprofits](https://github.com/solutions/industry/nonprofits)
  * By Industry
    * [Healthcare](https://github.com/solutions/industry/healthcare)
    * [Financial services](https://github.com/solutions/industry/financial-services)
    * [Manufacturing](https://github.com/solutions/industry/manufacturing)
    * [Government](https://github.com/solutions/industry/government)
    * [See all industries](https://github.com/solutions/industry)
  * Evaluate GitHub
    * [Why GitHub](https://github.com/why-github)
    * [Customer Stories](https://github.com/customer-stories)
    * [Business insights](https://github.com/solutions/executive-insights)
    * [Trust Center](https://github.com/trust-center)
  * Add-ons
    * [GitHub Advanced SecurityEnterprise-grade code security](https://github.com/security/advanced-security)
    * [Copilot for businessEnterprise-grade AI features](https://github.com/features/copilot/copilot-business)
    * [Premium SupportEnterprise-grade 24/7 support](https://github.com/enterprise/premium-support)
* Resources

  * Learn & Connect
    * [Documentation](https://docs.github.com/en)
    * [Resource center](https://github.com/resources)
    * [Blog](https://github.blog/)
    * [Events & webinars](https://github.com/resources/events)
    * [Community Forum](https://github.com/orgs/community/discussions)
    * [Customer Stories](https://github.com/customer-stories)
    * [Integrations](https://github.com/marketplace)
  * Support
    * [Customer support](https://help.github.com/)
    * [Training](https://learn.github.com/skills)
    * [GitHub Status](https://www.githubstatus.com/)
  * Company
    * [About](https://github.com/about)
    * [Partners](https://github.com/partners)
    * [Changelog](https://github.blog/changelog/)
  * GitHub Universe
    * [![](https://github.githubassets.com/assets/universe-a98cd54821b27569.png)![](https://github.githubassets.com/assets/universe-a98cd54821b27569.png)GitHub UniverseThe event for developers, by developers — talks, workshops, and what’s next for GitHub.](https://githubuniverse.com/)
* [Pricing](https://github.com/pricing)

Search/

[Sign in](/login?return%5Fto=https%3A%2F%2Fgithub.com%2Fsqlite%2Fsqlite%2Fblob%2Fmaster%2Fsrc%2Fwal.c)

[Sign up](/signup?ref%5Fcta=Sign+up&ref%5Floc=header+logged+out&ref%5Fpage=%2F%3Cuser-name%3E%2F%3Crepo-name%3E%2Fblob%2Fshow&source=header-repo&source%5Frepo=sqlite%2Fsqlite)

Appearance settings

You signed in with another tab or window. Reload to refresh your session. You signed out in another tab or window. Reload to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert 

{{ message }}

1. [sqlite](/sqlite)
2. [sqlite](/sqlite/sqlite)

## Repository navigation

* [Code](/sqlite/sqlite)
* [Pull requests26 (26)](/sqlite/sqlite/pulls)
* [Actions](/sqlite/sqlite/actions)
* [Security and quality](/sqlite/sqlite/security)
* [Insights](/sqlite/sqlite/pulse)

More items

[](/sqlite/sqlite) 

## FilesExpand file tree

master

## Breadcrumbs

1. [sqlite](/sqlite/sqlite/tree/master)
2. /[src](/sqlite/sqlite/tree/master/src)

/

# wal.c

Copy path

BlameMore file actions

BlameMore file actions

## Latest commit

## History

[History](/sqlite/sqlite/commits/master/src/wal.c)

History

4804 lines (4459 loc) · 180 KB

master

## Breadcrumbs

1. [sqlite](/sqlite/sqlite/tree/master)
2. /[src](/sqlite/sqlite/tree/master/src)

/

# wal.c

Copy path

Top

## File metadata and controls

* Code
* Blame

4804 lines (4459 loc) · 180 KB

[Raw](https://github.com/sqlite/sqlite/raw/refs/heads/master/src/wal.c)

Copy raw file

Download raw file

Open symbols panel

Edit and raw actions

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

84

85

86

87

88

89

90

91

92

93

94

95

96

97

98

99

100

101

102

103

104

105

106

107

108

109

110

111

112

113

114

115

116

117

118

119

120

121

122

123

124

125

126

127

128

129

130

131

132

133

134

135

136

137

138

139

140

141

142

143

144

145

146

147

148

149

150

151

152

153

154

155

156

157

158

159

160

161

162

163

164

165

166

167

168

169

170

171

172

173

174

175

176

177

178

179

180

181

182

183

184

185

186

187

188

189

190

191

192

193

194

195

196

197

198

199

200

201

202

203

204

205

206

207

208

209

210

211

212

213

214

215

216

217

218

219

220

221

222

223

224

225

226

227

228

229

230

231

232

233

234

235

236

237

238

239

240

241

242

243

244

245

246

247

248

249

250

251

252

253

254

255

256

257

258

259

260

261

262

263

264

265

266

267

268

269

270

271

272

273

274

275

276

277

278

279

280

281

282

283

284

285

286

287

288

289

290

291

292

293

294

295

296

297

298

299

300

301

302

303

304

305

306

307

308

309

310

311

312

313

314

315

316

317

318

319

320

321

322

323

324

325

326

327

328

329

330

331

332

333

334

335

336

337

338

339

340

341

342

343

344

345

346

347

348

349

350

351

352

353

354

355

356

357

358

359

360

361

362

363

364

365

366

367

368

369

370

371

372

373

374

375

376

377

378

379

380

381

382

383

384

385

386

387

388

389

390

391

392

393

394

395

396

397

398

399

400

401

402

403

404

405

406

407

408

409

410

411

412

413

414

415

416

417

418

419

420

421

422

423

424

425

426

427

428

429

430

431

432

433

434

435

436

437

438

439

440

441

442

443

444

445

446

447

448

449

450

451

452

453

454

455

456

457

458

459

460

461

462

463

464

465

466

467

468

469

470

471

472

473

474

475

476

477

478

479

480

481

482

483

484

485

486

487

488

489

490

491

492

493

494

495

496

497

498

499

500

501

502

503

504

505

506

507

508

509

510

511

512

513

514

515

516

517

518

519

520

521

522

523

524

525

526

527

528

529

530

531

532

533

534

535

536

537

538

539

540

541

542

543

544

545

546

547

548

549

550

551

552

553

554

555

556

557

558

559

560

561

562

563

564

565

566

567

568

569

570

571

572

573

574

575

576

577

578

579

580

581

582

583

584

585

586

587

588

589

590

591

592

593

594

595

596

597

598

599

600

601

602

603

604

605

606

607

608

609

610

611

612

613

614

615

616

617

618

619

620

621

622

623

624

625

626

627

628

629

630

631

632

633

634

635

636

637

638

639

640

641

642

643

644

645

646

647

648

649

650

651

652

653

654

655

656

657

658

659

660

661

662

663

664

665

666

667

668

669

670

671

672

673

674

675

676

677

678

679

680

681

682

683

684

685

686

687

688

689

690

691

692

693

694

695

696

697

698

699

700

701

702

703

704

705

706

707

708

709

710

711

712

713

714

715

716

717

718

719

720

721

722

723

724

725

726

727

728

729

730

731

732

733

734

735

736

737

738

739

740

741

742

743

744

745

746

747

748

749

750

751

752

753

754

755

756

757

758

759

760

761

762

763

764

765

766

767

768

769

770

771

772

773

774

775

776

777

778

779

780

781

782

783

784

785

786

787

788

789

790

791

792

793

794

795

796

797

798

799

800

801

802

803

804

805

806

807

808

809

810

811

812

813

814

815

816

817

818

819

820

821

822

823

824

825

826

827

828

829

830

831

832

833

834

835

836

837

838

839

840

841

842

843

844

845

846

847

848

849

850

851

852

853

854

855

856

857

858

859

860

861

862

863

864

865

866

867

868

869

870

871

872

873

874

875

876

877

878

879

880

881

882

883

884

885

886

887

888

889

890

891

892

893

894

895

896

897

898

899

900

901

902

903

904

905

906

907

908

909

910

911

912

913

914

915

916

917

918

919

920

921

922

923

924

925

926

927

928

929

930

931

932

933

934

935

936

937

938

939

940

941

942

943

944

945

946

947

948

949

950

951

952

953

954

955

956

957

958

959

960

961

962

963

964

965

966

967

968

969

970

971

972

973

974

975

976

977

978

979

980

981

982

983

984

985

986

987

988

989

990

991

992

993

994

995

996

997

998

999

1000

/\*

\*\* 2010 February 1

\*\*

\*\* The author disclaims copyright to this source code. In place of

\*\* a legal notice, here is a blessing:

\*\*

\*\* May you do good and not evil.

\*\* May you find forgiveness for yourself and forgive others.

\*\* May you share freely, never taking more than you give.

\*\*

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

\*\*

\*\* This file contains the implementation of a write-ahead log (WAL) used in

\*\* "journal\_mode=WAL" mode.

\*\*

\*\* WRITE-AHEAD LOG (WAL) FILE FORMAT

\*\*

\*\* A WAL file consists of a header followed by zero or more "frames".

\*\* Each frame records the revised content of a single page from the

\*\* database file. All changes to the database are recorded by writing

\*\* frames into the WAL. Transactions commit when a frame is written that

\*\* contains a commit marker. A single WAL can and usually does record

\*\* multiple transactions. Periodically, the content of the WAL is

\*\* transferred back into the database file in an operation called a

\*\* "checkpoint".

\*\*

\*\* A single WAL file can be used multiple times. In other words, the

\*\* WAL can fill up with frames and then be checkpointed and then new

\*\* frames can overwrite the old ones. A WAL always grows from beginning

\*\* toward the end. Checksums and counters attached to each frame are

\*\* used to determine which frames within the WAL are valid and which

\*\* are leftovers from prior checkpoints.

\*\*

\*\* The WAL header is 32 bytes in size and consists of the following eight

\*\* big-endian 32-bit unsigned integer values:

\*\*

\*\* 0: Magic number. 0x377f0682 or 0x377f0683

\*\* 4: File format version. Currently 3007000

\*\* 8: Database page size. Example: 1024

\*\* 12: Checkpoint sequence number

\*\* 16: Salt-1, random integer incremented with each checkpoint

\*\* 20: Salt-2, a different random integer changing with each ckpt

\*\* 24: Checksum-1 (first part of checksum for first 24 bytes of header).

\*\* 28: Checksum-2 (second part of checksum for first 24 bytes of header).

\*\*

\*\* Immediately following the wal-header are zero or more frames. Each

\*\* frame consists of a 24-byte frame-header followed by <page-size> bytes

\*\* of page data. The frame-header is six big-endian 32-bit unsigned

\*\* integer values, as follows:

\*\*

\*\* 0: Page number.

\*\* 4: For commit records, the size of the database image in pages

\*\* after the commit. For all other records, zero.

\*\* 8: Salt-1 (copied from the header)

\*\* 12: Salt-2 (copied from the header)

\*\* 16: Checksum-1.

\*\* 20: Checksum-2.

\*\*

\*\* A frame is considered valid if and only if the following conditions are

\*\* true:

\*\*

\*\* (1) The salt-1 and salt-2 values in the frame-header match

\*\* salt values in the wal-header

\*\*

\*\* (2) The checksum values in the final 8 bytes of the frame-header

\*\* exactly match the checksum computed consecutively on the

\*\* WAL header and the first 8 bytes and the content of all frames

\*\* up to and including the current frame.

\*\*

\*\* The checksum is computed using 32-bit big-endian integers if the

\*\* magic number in the first 4 bytes of the WAL is 0x377f0683 and it

\*\* is computed using little-endian if the magic number is 0x377f0682.

\*\* The checksum values are always stored in the frame header in a

\*\* big-endian format regardless of which byte order is used to compute

\*\* the checksum. The checksum is computed by interpreting the input as

\*\* an even number of unsigned 32-bit integers: x\[0\] through x\[N\]. The

\*\* algorithm used for the checksum is as follows:

\*\*

\*\* for i from 0 to n-1 step 2:

\*\* s0 += x\[i\] + s1;

\*\* s1 += x\[i+1\] + s0;

\*\* endfor

\*\*

\*\* Note that s0 and s1 are both weighted checksums using fibonacci weights

\*\* in reverse order (the largest fibonacci weight occurs on the first element

\*\* of the sequence being summed.) The s1 value spans all 32-bit

\*\* terms of the sequence whereas s0 omits the final term.

\*\*

\*\* On a checkpoint, the WAL is first VFS.xSync-ed, then valid content of the

\*\* WAL is transferred into the database, then the database is VFS.xSync-ed.

\*\* The VFS.xSync operations serve as write barriers - all writes launched

\*\* before the xSync must complete before any write that launches after the

\*\* xSync begins.

\*\*

\*\* After each checkpoint, the salt-1 value is incremented and the salt-2

\*\* value is randomized. This prevents old and new frames in the WAL from

\*\* being considered valid at the same time and being checkpointing together

\*\* following a crash.

\*\*

\*\* READER ALGORITHM

\*\*

\*\* To read a page from the database (call it page number P), a reader

\*\* first checks the WAL to see if it contains page P. If so, then the

\*\* last valid instance of page P that is a followed by a commit frame

\*\* or is a commit frame itself becomes the value read. If the WAL

\*\* contains no copies of page P that are valid and which are a commit

\*\* frame or are followed by a commit frame, then page P is read from

\*\* the database file.

\*\*

\*\* To start a read transaction, the reader records the index of the last

\*\* valid frame in the WAL. The reader uses this recorded "mxFrame" value

\*\* for all subsequent read operations. New transactions can be appended

\*\* to the WAL, but as long as the reader uses its original mxFrame value

\*\* and ignores the newly appended content, it will see a consistent snapshot

\*\* of the database from a single point in time. This technique allows

\*\* multiple concurrent readers to view different versions of the database

\*\* content simultaneously.

\*\*

\*\* The reader algorithm in the previous paragraphs works correctly, but

\*\* because frames for page P can appear anywhere within the WAL, the

\*\* reader has to scan the entire WAL looking for page P frames. If the

\*\* WAL is large (multiple megabytes is typical) that scan can be slow,

\*\* and read performance suffers. To overcome this problem, a separate

\*\* data structure called the wal-index is maintained to expedite the

\*\* search for frames of a particular page.

\*\*

\*\* WAL-INDEX FORMAT

\*\*

\*\* Conceptually, the wal-index is shared memory, though VFS implementations

\*\* might choose to implement the wal-index using a mmapped file. Because

\*\* the wal-index is shared memory, SQLite does not support journal\_mode=WAL

\*\* on a network filesystem. All users of the database must be able to

\*\* share memory.

\*\*

\*\* In the default unix and windows implementation, the wal-index is a mmapped

\*\* file whose name is the database name with a "-shm" suffix added. For that

\*\* reason, the wal-index is sometimes called the "shm" file.

\*\*

\*\* The wal-index is transient. After a crash, the wal-index can (and should

\*\* be) reconstructed from the original WAL file. In fact, the VFS is required

\*\* to either truncate or zero the header of the wal-index when the last

\*\* connection to it closes. Because the wal-index is transient, it can

\*\* use an architecture-specific format; it does not have to be cross-platform.

\*\* Hence, unlike the database and WAL file formats which store all values

\*\* as big endian, the wal-index can store multi-byte values in the native

\*\* byte order of the host computer.

\*\*

\*\* The purpose of the wal-index is to answer this question quickly: Given

\*\* a page number P and a maximum frame index M, return the index of the

\*\* last frame in the wal before frame M for page P in the WAL, or return

\*\* NULL if there are no frames for page P in the WAL prior to M.

\*\*

\*\* The wal-index consists of a header region, followed by an one or

\*\* more index blocks.

\*\*

\*\* The wal-index header contains the total number of frames within the WAL

\*\* in the mxFrame field.

\*\*

\*\* Each index block except for the first contains information on

\*\* HASHTABLE\_NPAGE frames. The first index block contains information on

\*\* HASHTABLE\_NPAGE\_ONE frames. The values of HASHTABLE\_NPAGE\_ONE and

\*\* HASHTABLE\_NPAGE are selected so that together the wal-index header and

\*\* first index block are the same size as all other index blocks in the

\*\* wal-index. The values are:

\*\*

\*\* HASHTABLE\_NPAGE 4096

\*\* HASHTABLE\_NPAGE\_ONE 4062

\*\*

\*\* Each index block contains two sections, a page-mapping that contains the

\*\* database page number associated with each wal frame, and a hash-table

\*\* that allows readers to query an index block for a specific page number.

\*\* The page-mapping is an array of HASHTABLE\_NPAGE (or HASHTABLE\_NPAGE\_ONE

\*\* for the first index block) 32-bit page numbers. The first entry in the

\*\* first index-block contains the database page number corresponding to the

\*\* first frame in the WAL file. The first entry in the second index block

\*\* in the WAL file corresponds to the (HASHTABLE\_NPAGE\_ONE+1)th frame in

\*\* the log, and so on.

\*\*

\*\* The last index block in a wal-index usually contains less than the full

\*\* complement of HASHTABLE\_NPAGE (or HASHTABLE\_NPAGE\_ONE) page-numbers,

\*\* depending on the contents of the WAL file. This does not change the

\*\* allocated size of the page-mapping array - the page-mapping array merely

\*\* contains unused entries.

\*\*

\*\* Even without using the hash table, the last frame for page P

\*\* can be found by scanning the page-mapping sections of each index block

\*\* starting with the last index block and moving toward the first, and

\*\* within each index block, starting at the end and moving toward the

\*\* beginning. The first entry that equals P corresponds to the frame

\*\* holding the content for that page.

\*\*

\*\* The hash table consists of HASHTABLE\_NSLOT 16-bit unsigned integers.

\*\* HASHTABLE\_NSLOT = 2\*HASHTABLE\_NPAGE, and there is one entry in the

\*\* hash table for each page number in the mapping section, so the hash

\*\* table is never more than half full. The expected number of collisions

\*\* prior to finding a match is 1\. Each entry of the hash table is an

\*\* 1-based index of an entry in the mapping section of the same

\*\* index block. Let K be the 1-based index of the largest entry in

\*\* the mapping section. (For index blocks other than the last, K will

\*\* always be exactly HASHTABLE\_NPAGE (4096) and for the last index block

\*\* K will be (mxFrame%HASHTABLE\_NPAGE).) Unused slots of the hash table

\*\* contain a value of 0.

\*\*

\*\* To look for page P in the hash table, first compute a hash iKey on

\*\* P as follows:

\*\*

\*\* iKey = (P \* 383) % HASHTABLE\_NSLOT

\*\*

\*\* Then start scanning entries of the hash table, starting with iKey

\*\* (wrapping around to the beginning when the end of the hash table is

\*\* reached) until an unused hash slot is found. Let the first unused slot

\*\* be at index iUnused. (iUnused might be less than iKey if there was

\*\* wrap-around.) Because the hash table is never more than half full,

\*\* the search is guaranteed to eventually hit an unused entry. Let

\*\* iMax be the value between iKey and iUnused, closest to iUnused,

\*\* where aHash\[iMax\]==P. If there is no iMax entry (if there exists

\*\* no hash slot such that aHash\[i\]==p) then page P is not in the

\*\* current index block. Otherwise the iMax-th mapping entry of the

\*\* current index block corresponds to the last entry that references

\*\* page P.

\*\*

\*\* A hash search begins with the last index block and moves toward the

\*\* first index block, looking for entries corresponding to page P. On

\*\* average, only two or three slots in each index block need to be

\*\* examined in order to either find the last entry for page P, or to

\*\* establish that no such entry exists in the block. Each index block

\*\* holds over 4000 entries. So two or three index blocks are sufficient

\*\* to cover a typical 10 megabyte WAL file, assuming 1K pages. 8 or 10

\*\* comparisons (on average) suffice to either locate a frame in the

\*\* WAL or to establish that the frame does not exist in the WAL. This

\*\* is much faster than scanning the entire 10MB WAL.

\*\*

\*\* Note that entries are added in order of increasing K. Hence, one

\*\* reader might be using some value K0 and a second reader that started

\*\* at a later time (after additional transactions were added to the WAL

\*\* and to the wal-index) might be using a different value K1, where K1>K0.

\*\* Both readers can use the same hash table and mapping section to get

\*\* the correct result. There may be entries in the hash table with

\*\* K>K0 but to the first reader, those entries will appear to be unused

\*\* slots in the hash table and so the first reader will get an answer as

\*\* if no values greater than K0 had ever been inserted into the hash table

\*\* in the first place - which is what reader one wants. Meanwhile, the

\*\* second reader using K1 will see additional values that were inserted

\*\* later, which is exactly what reader two wants.

\*\*

\*\* When a rollback occurs, the value of K is decreased. Hash table entries

\*\* that correspond to frames greater than the new K value are removed

\*\* from the hash table at this point.

\*/

#ifndef SQLITE\_OMIT\_WAL

#include "wal.h"

/\*

\*\* Trace output macros

\*/

#if defined(SQLITE\_TEST) && defined(SQLITE\_DEBUG)

int sqlite3WalTrace \= 0;

\# define WALTRACE(X) if(sqlite3WalTrace) sqlite3DebugPrintf X

#else

\# define WALTRACE(X)

#endif

/\*

\*\* The maximum (and only) versions of the wal and wal-index formats

\*\* that may be interpreted by this version of SQLite.

\*\*

\*\* If a client begins recovering a WAL file and finds that (a) the checksum

\*\* values in the wal-header are correct and (b) the version field is not

\*\* WAL\_MAX\_VERSION, recovery fails and SQLite returns SQLITE\_CANTOPEN.

\*\*

\*\* Similarly, if a client successfully reads a wal-index header (i.e. the

\*\* checksum test is successful) and finds that the version field is not

\*\* WALINDEX\_MAX\_VERSION, then no read-transaction is opened and SQLite

\*\* returns SQLITE\_CANTOPEN.

\*/

#define WAL\_MAX\_VERSION 3007000

#define WALINDEX\_MAX\_VERSION 3007000

/\*

\*\* Index numbers for various locking bytes. WAL\_NREADER is the number

\*\* of available reader locks and should be at least 3\. The default

\*\* is SQLITE\_SHM\_NLOCK==8 and WAL\_NREADER==5.

\*\*

\*\* Technically, the various VFSes are free to implement these locks however

\*\* they see fit. However, compatibility is encouraged so that VFSes can

\*\* interoperate. The standard implementation used on both unix and windows

\*\* is for the index number to indicate a byte offset into the

\*\* WalCkptInfo.aLock\[\] array in the wal-index header. In other words, all

\*\* locks are on the shm file. The WALINDEX\_LOCK\_OFFSET constant (which

\*\* should be 120) is the location in the shm file for the first locking

\*\* byte.

\*/

#define WAL\_WRITE\_LOCK 0

#define WAL\_ALL\_BUT\_WRITE 1

#define WAL\_CKPT\_LOCK 1

#define WAL\_RECOVER\_LOCK 2

#define WAL\_READ\_LOCK(I) (3+(I))

#define WAL\_NREADER (SQLITE\_SHM\_NLOCK-3)

/\* Object declarations \*/

typedef struct WalIndexHdr WalIndexHdr;

typedef struct WalIterator WalIterator;

typedef struct WalCkptInfo WalCkptInfo;

/\*

\*\* The following object holds a copy of the wal-index header content.

\*\*

\*\* The actual header in the wal-index consists of two copies of this

\*\* object followed by one instance of the WalCkptInfo object.

\*\* For all versions of SQLite through 3.10.0 and probably beyond,

\*\* the locking bytes (WalCkptInfo.aLock) start at offset 120 and

\*\* the total header size is 136 bytes.

\*\*

\*\* The szPage value can be any power of 2 between 512 and 32768, inclusive.

\*\* Or it can be 1 to represent a 65536-byte page. The latter case was

\*\* added in 3.7.1 when support for 64K pages was added.

\*/

struct WalIndexHdr {

u32 iVersion; /\* Wal-index version \*/

u32 unused; /\* Unused (padding) field \*/

u32 iChange; /\* Counter incremented each transaction \*/

u8 isInit; /\* 1 when initialized \*/

u8 bigEndCksum; /\* True if checksums in WAL are big-endian \*/

u16 szPage; /\* Database page size in bytes. 1==64K \*/

u32 mxFrame; /\* Index of last valid frame in the WAL \*/

u32 nPage; /\* Size of database in pages \*/

u32 aFrameCksum\[2\]; /\* Checksum of last frame in log \*/

u32 aSalt\[2\]; /\* Two salt values copied from WAL header \*/

u32 aCksum\[2\]; /\* Checksum over all prior fields \*/

};

/\*

\*\* A copy of the following object occurs in the wal-index immediately

\*\* following the second copy of the WalIndexHdr. This object stores

\*\* information used by checkpoint.

\*\*

\*\* nBackfill is the number of frames in the WAL that have been written

\*\* back into the database. (We call the act of moving content from WAL to

\*\* database "backfilling".) The nBackfill number is never greater than

\*\* WalIndexHdr.mxFrame. nBackfill can only be increased by threads

\*\* holding the WAL\_CKPT\_LOCK lock (which includes a recovery thread).

\*\* However, a WAL\_WRITE\_LOCK thread can move the value of nBackfill from

\*\* mxFrame back to zero when the WAL is reset.

\*\*

\*\* nBackfillAttempted is the largest value of nBackfill that a checkpoint

\*\* has attempted to achieve. Normally nBackfill==nBackfillAtempted, however

\*\* the nBackfillAttempted is set before any backfilling is done and the

\*\* nBackfill is only set after all backfilling completes. So if a checkpoint

\*\* crashes, nBackfillAttempted might be larger than nBackfill. The

\*\* WalIndexHdr.mxFrame must never be less than nBackfillAttempted.

\*\*

\*\* The aLock\[\] field is a set of bytes used for locking. These bytes should

\*\* never be read or written.

\*\*

\*\* There is one entry in aReadMark\[\] for each reader lock. If a reader

\*\* holds read-lock K, then the value in aReadMark\[K\] is no greater than

\*\* the mxFrame for that reader. The value READMARK\_NOT\_USED (0xffffffff)

\*\* for any aReadMark\[\] means that entry is unused. aReadMark\[0\] is

\*\* a special case; its value is never used and it exists as a place-holder

\*\* to avoid having to offset aReadMark\[\] indexes by one. Readers holding

\*\* WAL\_READ\_LOCK(0) always ignore the entire WAL and read all content

\*\* directly from the database.

\*\*

\*\* The value of aReadMark\[K\] may only be changed by a thread that

\*\* is holding an exclusive lock on WAL\_READ\_LOCK(K). Thus, the value of

\*\* aReadMark\[K\] cannot changed while there is a reader is using that mark

\*\* since the reader will be holding a shared lock on WAL\_READ\_LOCK(K).

\*\*

\*\* The checkpointer may only transfer frames from WAL to database where

\*\* the frame numbers are less than or equal to every aReadMark\[\] that is

\*\* in use (that is, every aReadMark\[j\] for which there is a corresponding

\*\* WAL\_READ\_LOCK(j)). New readers (usually) pick the aReadMark\[\] with the

\*\* largest value and will increase an unused aReadMark\[\] to mxFrame if there

\*\* is not already an aReadMark\[\] equal to mxFrame. The exception to the

\*\* previous sentence is when nBackfill equals mxFrame (meaning that everything

\*\* in the WAL has been backfilled into the database) then new readers

\*\* will choose aReadMark\[0\] which has value 0 and hence such reader will

\*\* get all their all content directly from the database file and ignore

\*\* the WAL.

\*\*

\*\* Writers normally append new frames to the end of the WAL. However,

\*\* if nBackfill equals mxFrame (meaning that all WAL content has been

\*\* written back into the database) and if no readers are using the WAL

\*\* (in other words, if there are no WAL\_READ\_LOCK(i) where i>0) then

\*\* the writer will first "reset" the WAL back to the beginning and start

\*\* writing new content beginning at frame 1.

\*\*

\*\* We assume that 32-bit loads are atomic and so no locks are needed in

\*\* order to read from any aReadMark\[\] entries.

\*/

struct WalCkptInfo {

u32 nBackfill; /\* Number of WAL frames backfilled into DB \*/

u32 aReadMark\[WAL\_NREADER\]; /\* Reader marks \*/

u8 aLock\[SQLITE\_SHM\_NLOCK\]; /\* Reserved space for locks \*/

u32 nBackfillAttempted; /\* WAL frames perhaps written, or maybe not \*/

u32 notUsed0; /\* Available for future enhancements \*/

};

#define READMARK\_NOT\_USED 0xffffffff

/\*

\*\* This is a schematic view of the complete 136-byte header of the

\*\* wal-index file (also known as the -shm file):

\*\*

\*\* +-----------------------------+

\*\* 0: | iVersion | \\

\*\* +-----------------------------+ |

\*\* 4: | (unused padding) | |

\*\* +-----------------------------+ |

\*\* 8: | iChange | |

\*\* +-------+-------+-------------+ |

\*\* 12: | bInit | bBig | szPage | |

\*\* +-------+-------+-------------+ |

\*\* 16: | mxFrame | | First copy of the

\*\* +-----------------------------+ | WalIndexHdr object

\*\* 20: | nPage | |

\*\* +-----------------------------+ |

\*\* 24: | aFrameCksum | |

\*\* | | |

\*\* +-----------------------------+ |

\*\* 32: | aSalt | |

\*\* | | |

\*\* +-----------------------------+ |

\*\* 40: | aCksum | |

\*\* | | /

\*\* +-----------------------------+

\*\* 48: | iVersion | \\

\*\* +-----------------------------+ |

\*\* 52: | (unused padding) | |

\*\* +-----------------------------+ |

\*\* 56: | iChange | |

\*\* +-------+-------+-------------+ |

\*\* 60: | bInit | bBig | szPage | |

\*\* +-------+-------+-------------+ | Second copy of the

\*\* 64: | mxFrame | | WalIndexHdr

\*\* +-----------------------------+ |

\*\* 68: | nPage | |

\*\* +-----------------------------+ |

\*\* 72: | aFrameCksum | |

\*\* | | |

\*\* +-----------------------------+ |

\*\* 80: | aSalt | |

\*\* | | |

\*\* +-----------------------------+ |

\*\* 88: | aCksum | |

\*\* | | /

\*\* +-----------------------------+

\*\* 96: | nBackfill |

\*\* +-----------------------------+

\*\* 100: | 5 read marks |

\*\* | |

\*\* | |

\*\* | |

\*\* | |

\*\* +-------+-------+------+------+

\*\* 120: | Write | Ckpt | Rcvr | Rd0 | \\

\*\* +-------+-------+------+------+ ) 8 lock bytes

\*\* | Read1 | Read2 | Rd3 | Rd4 | /

\*\* +-------+-------+------+------+

\*\* 128: | nBackfillAttempted |

\*\* +-----------------------------+

\*\* 132: | (unused padding) |

\*\* +-----------------------------+

\*/

/\* A block of WALINDEX\_LOCK\_RESERVED bytes beginning at

\*\* WALINDEX\_LOCK\_OFFSET is reserved for locks. Since some systems

\*\* only support mandatory file-locks, we do not read or write data

\*\* from the region of the file on which locks are applied.

\*/

#define WALINDEX\_LOCK\_OFFSET (sizeof(WalIndexHdr)\*2+offsetof(WalCkptInfo,aLock))

#define WALINDEX\_HDR\_SIZE (sizeof(WalIndexHdr)\*2+sizeof(WalCkptInfo))

/\* Size of header before each frame in wal \*/

#define WAL\_FRAME\_HDRSIZE 24

/\* Size of write ahead log header, including checksum. \*/

#define WAL\_HDRSIZE 32

/\* WAL magic value. Either this value, or the same value with the least

\*\* significant bit also set (WAL\_MAGIC | 0x00000001) is stored in 32-bit

\*\* big-endian format in the first 4 bytes of a WAL file.

\*\*

\*\* If the LSB is set, then the checksums for each frame within the WAL

\*\* file are calculated by treating all data as an array of 32-bit

\*\* big-endian words. Otherwise, they are calculated by interpreting

\*\* all data as 32-bit little-endian words.

\*/

#define WAL\_MAGIC 0x377f0682

/\*

\*\* Return the offset of frame iFrame in the write-ahead log file,

\*\* assuming a database page size of szPage bytes. The offset returned

\*\* is to the start of the write-ahead log frame-header.

\*/

#define walFrameOffset(iFrame, szPage) ( \\

 WAL\_HDRSIZE + ((iFrame)-1)\*(i64)((szPage)+WAL\_FRAME\_HDRSIZE) \\

)

/\*

\*\* An open write-ahead log file is represented by an instance of the

\*\* following object.

\*\*

\*\* writeLock:

\*\* This is usually set to 1 whenever the WRITER lock is held. However,

\*\* if it is set to 2, then the WRITER lock is held but must be released

\*\* by walHandleException() if a SEH exception is thrown.

\*/

struct Wal {

sqlite3\_vfs \*pVfs; /\* The VFS used to create pDbFd \*/

sqlite3\_file \*pDbFd; /\* File handle for the database file \*/

sqlite3\_file \*pWalFd; /\* File handle for WAL file \*/

u32 iCallback; /\* Value to pass to log callback (or 0) \*/

i64 mxWalSize; /\* Truncate WAL to this size upon reset \*/

int nWiData; /\* Size of array apWiData \*/

int szFirstBlock; /\* Size of first block written to WAL file \*/

volatile u32 \*\*apWiData; /\* Pointer to wal-index content in memory \*/

u32 szPage; /\* Database page size \*/

i16 readLock; /\* Which read lock is being held. -1 for none \*/

u8 syncFlags; /\* Flags to use to sync header writes \*/

u8 exclusiveMode; /\* Non-zero if connection is in exclusive mode \*/

u8 writeLock; /\* True if in a write transaction \*/

u8 ckptLock; /\* True if holding a checkpoint lock \*/

u8 readOnly; /\* WAL\_RDWR, WAL\_RDONLY, or WAL\_SHM\_RDONLY \*/

u8 truncateOnCommit; /\* True to truncate WAL file on commit \*/

u8 syncHeader; /\* Fsync the WAL header if true \*/

u8 padToSectorBoundary; /\* Pad transactions out to the next sector \*/

u8 bShmUnreliable; /\* SHM content is read-only and unreliable \*/

WalIndexHdr hdr; /\* Wal-index header for current transaction \*/

u32 minFrame; /\* Ignore wal frames before this one \*/

u32 iReCksum; /\* On commit, recalculate checksums from here \*/

const char \*zWalName; /\* Name of WAL file \*/

u32 nCkpt; /\* Checkpoint sequence counter in the wal-header \*/

#ifdef SQLITE\_USE\_SEH

u32 lockMask; /\* Mask of locks held \*/

void \*pFree; /\* Pointer to sqlite3\_free() if exception thrown \*/

u32 \*pWiValue; /\* Value to write into apWiData\[iWiPg\] \*/

int iWiPg; /\* Write pWiValue into apWiData\[iWiPg\] \*/

int iSysErrno; /\* System error code following exception \*/

#endif

#ifdef SQLITE\_DEBUG

int nSehTry; /\* Number of nested SEH\_TRY{} blocks \*/

u8 lockError; /\* True if a locking error has occurred \*/

#endif

#ifdef SQLITE\_ENABLE\_SNAPSHOT

WalIndexHdr \*pSnapshot; /\* Start transaction here if not NULL \*/

int bGetSnapshot; /\* Transaction opened for sqlite3\_get\_snapshot() \*/

#endif

#ifdef SQLITE\_ENABLE\_SETLK\_TIMEOUT

sqlite3 \*db;

#endif

};

/\*

\*\* Candidate values for Wal.exclusiveMode.

\*/

#define WAL\_NORMAL\_MODE 0

#define WAL\_EXCLUSIVE\_MODE 1

#define WAL\_HEAPMEMORY\_MODE 2

/\*

\*\* Possible values for WAL.readOnly

\*/

#define WAL\_RDWR 0 /\* Normal read/write connection \*/

#define WAL\_RDONLY 1 /\* The WAL file is readonly \*/

#define WAL\_SHM\_RDONLY 2 /\* The SHM file is readonly \*/

/\*

\*\* Each page of the wal-index mapping contains a hash-table made up of

\*\* an array of HASHTABLE\_NSLOT elements of the following type.

\*/

typedef u16 ht\_slot;

/\*

\*\* This structure is used to implement an iterator that loops through

\*\* all frames in the WAL in database page order. Where two or more frames

\*\* correspond to the same database page, the iterator visits only the

\*\* frame most recently written to the WAL (in other words, the frame with

\*\* the largest index).

\*\*

\*\* The internals of this structure are only accessed by:

\*\*

\*\* walIteratorInit() - Create a new iterator,

\*\* walIteratorNext() - Step an iterator,

\*\* walIteratorFree() - Free an iterator.

\*\*

\*\* This functionality is used by the checkpoint code (see walCheckpoint()).

\*\*

\*\* There are two possible algorithms:

\*\*

\*\* WALITER-1 Load all pages mentioned in the WAL file and sort them,

\*\* then hand them back out in sorted order as requested by

\*\* walIteratorNext(). nPagemap==0 for this algorithm.

\*\*

\*\* WALITER-2 Create a map of all database file pages and record the

\*\* last WAL file frame that updates that page. Then walk

\*\* through the map in acsending order and return all

\*\* non-zero entries. nPagemap is positive for this algorithm.

\*\*

\*\* Either algorithm should work for any database and WAL file, however

\*\* algorithm WALITER-1 is faster and uses less memory when the database is

\*\* larger than the WAL file and algorithm WALITER-2 is faster and uses

\*\* less memory when the WAL file is larger than the database, modulo a

\*\* constant of proportionality. The walIteratorInit() routine selects

\*\* the best algorithm for each situation. WALITER-2 was added for

\*\* SQLite 3.54.0\. Prior to that, WALITER-1 was used always.

\*\* 

\*\* For algorithm WALITER-2, nPagemap stores the number of pages in the

\*\* database file, nSegment==1, and aSegment\[0\].aPgno\[\] is the page map array

\*\* that is nPagemap+1 entries in length. The value of aSegment\[0\].aPgno\[PGNO\]

\*\* is the frame number of the last (newest) entry for page PGNO in the WAL

\*\* file, or 0 if PGNO is not in the WAL file. (Aside: There is no page

\*\* number 0 in a well-formed database, so the memory allocation is arranged

\*\* such that aSegment\[0\].aPgno\[0\] and aSegment\[0\].iZero are aliases for the

\*\* same four bits of memory. This saves us from having to use -1 and +1

\*\* offsets to translate between 1-based SQLite page numbers and 0-based

\*\* C-language index numbers. tag-20260903-1)

\*/

struct WalIterator {

u32 iPrior; /\* Last result returned from the iterator \*/

int nSegment; /\* Number of entries in aSegment\[\] \*/

u32 nPagemap; /\* Non-zero in "page-map" mode \*/

struct WalSegment {

int iNext; /\* Next slot in aIndex\[\] not yet returned \*/

ht\_slot \*aIndex; /\* i0, i1, i2... such that aPgno\[iN\] ascend \*/

u32 \*aPgno; /\* Array of page numbers. \*/

int nEntry; /\* Nr. of entries in aPgno\[\] and aIndex\[\] \*/

int iZero; /\* Frame number associated with aPgno\[0\] \*/

 } aSegment\[FLEXARRAY\]; /\* One for every 32KB page in the wal-index \*/

};

/\* Size (in bytes) of a WalIterator object suitable for N or fewer segments \*/

#define SZ\_WALITERATOR(N) \\

 (offsetof(WalIterator,aSegment)+(N)\*sizeof(struct WalSegment))

/\*

\*\* Define the parameters of the hash tables in the wal-index file. There

\*\* is a hash-table following every HASHTABLE\_NPAGE page numbers in the

\*\* wal-index.

\*\*

\*\* Changing any of these constants will alter the wal-index format and

\*\* create incompatibilities.

\*/

#define HASHTABLE\_NPAGE 4096 /\* Must be power of 2 \*/

#define HASHTABLE\_HASH\_1 383 /\* Should be prime \*/

#define HASHTABLE\_NSLOT (HASHTABLE\_NPAGE\*2) /\* Must be a power of 2 \*/

/\*

\*\* The block of page numbers associated with the first hash-table in a

\*\* wal-index is smaller than usual. This is so that there is a complete

\*\* hash-table on each aligned 32KB page of the wal-index.

\*/

#define HASHTABLE\_NPAGE\_ONE (HASHTABLE\_NPAGE - (WALINDEX\_HDR\_SIZE/sizeof(u32)))

/\* The wal-index is divided into pages of WALINDEX\_PGSZ bytes each. \*/

#define WALINDEX\_PGSZ ( \\

 sizeof(ht\_slot)\*HASHTABLE\_NSLOT + HASHTABLE\_NPAGE\*sizeof(u32) \\

)

/\*

\*\* Structured Exception Handling (SEH) is a Windows-specific technique

\*\* for catching exceptions raised while accessing memory-mapped files.

\*\*

\*\* The -DSQLITE\_USE\_SEH compile-time option means to use SEH to catch and

\*\* deal with system-level errors that arise during WAL -shm file processing.

\*\* Without this compile-time option, any system-level faults that appear

\*\* while accessing the memory-mapped -shm file will cause a process-wide

\*\* signal to be deliver, which will more than likely cause the entire

\*\* process to exit.

\*/

#ifdef SQLITE\_USE\_SEH

#include <Windows.h>

/\* Beginning of a block of code in which an exception might occur \*/

\# define SEH\_TRY \_\_try { \\

 assert( walAssertLockmask(pWal) && pWal->nSehTry==0 ); \\

 VVA\_ONLY(pWal->nSehTry++);

/\* The end of a block of code in which an exception might occur \*/

\# define SEH\_EXCEPT(X) \\

 VVA\_ONLY(pWal->nSehTry--); \\

 assert( pWal->nSehTry==0 ); \\

 } \_\_except( sehExceptionFilter(pWal, GetExceptionCode(), GetExceptionInformation() ) ){ X }

/\* Simulate a memory-mapping fault in the -shm file for testing purposes \*/

\# define SEH\_INJECT\_FAULT sehInjectFault(pWal) 

/\*

\*\* The second argument is the return value of GetExceptionCode() for the 

\*\* current exception. Return EXCEPTION\_EXECUTE\_HANDLER if the exception code

\*\* indicates that the exception may have been caused by accessing the \*-shm 

\*\* file mapping. Or EXCEPTION\_CONTINUE\_SEARCH otherwise.

\*/

static int sehExceptionFilter(Wal \*pWal, int eCode, EXCEPTION\_POINTERS \*p){

VVA\_ONLY(pWal\->nSehTry\--);

if( eCode\==EXCEPTION\_IN\_PAGE\_ERROR ){

if( p && p\->ExceptionRecord && p\->ExceptionRecord\->NumberParameters\>=3 ){

/\* From MSDN: For this type of exception, the first element of the

 \*\* ExceptionInformation\[\] array is a read-write flag - 0 if the exception

 \*\* was thrown while reading, 1 if while writing. The second element is

 \*\* the virtual address being accessed. The "third array element specifies

 \*\* the underlying NTSTATUS code that resulted in the exception". \*/

pWal\->iSysErrno \= (int)p\->ExceptionRecord\->ExceptionInformation\[2\];

 }

return EXCEPTION\_EXECUTE\_HANDLER;

 }

return EXCEPTION\_CONTINUE\_SEARCH;

}

/\*

\*\* If one is configured, invoke the xTestCallback callback with 650 as

\*\* the argument. If it returns true, throw the same exception that is

\*\* thrown by the system if the \*-shm file mapping is accessed after it

\*\* has been invalidated.

\*/

static void sehInjectFault(Wal \*pWal){

int res;

assert( pWal\->nSehTry\>0 );

res \= sqlite3FaultSim(650);

if( res!=0 ){

ULONG\_PTR aArg\[3\];

aArg\[0\] \= 0;

aArg\[1\] \= 0;

aArg\[2\] \= (ULONG\_PTR)res;

RaiseException(EXCEPTION\_IN\_PAGE\_ERROR, 0, 3, (const ULONG\_PTR\*)aArg);

 }

}

/\*

\*\* There are two ways to use this macro. To set a pointer to be freed

\*\* if an exception is thrown:

\*\*

\*\* SEH\_FREE\_ON\_ERROR(0, pPtr);

\*\*

\*\* and to cancel the same:

\*\*

\*\* SEH\_FREE\_ON\_ERROR(pPtr, 0);

\*\*

\*\* In the first case, there must not already be a pointer registered to

\*\* be freed. In the second case, pPtr must be the registered pointer.

\*/

#define SEH\_FREE\_ON\_ERROR(X,Y) \\

 assert( (X==0 || Y==0) && pWal->pFree==X ); pWal->pFree = Y

/\*

\*\* There are two ways to use this macro. To arrange for pWal->apWiData\[iPg\]

\*\* to be set to pValue if an exception is thrown:

\*\*

\*\* SEH\_SET\_ON\_ERROR(iPg, pValue);

\*\*

\*\* and to cancel the same:

\*\*

\*\* SEH\_SET\_ON\_ERROR(0, 0);

\*/

#define SEH\_SET\_ON\_ERROR(X,Y) pWal->iWiPg = X; pWal->pWiValue = Y

#else

\# define SEH\_TRY VVA\_ONLY(pWal->nSehTry++);

\# define SEH\_EXCEPT(X) VVA\_ONLY(pWal->nSehTry--); assert( pWal->nSehTry==0 );

\# define SEH\_INJECT\_FAULT assert( pWal->nSehTry>0 );

\# define SEH\_FREE\_ON\_ERROR(X,Y)

\# define SEH\_SET\_ON\_ERROR(X,Y)

#endif /\* ifdef SQLITE\_USE\_SEH \*/

/\*

\*\* Obtain a pointer to the iPage'th page of the wal-index. The wal-index

\*\* is broken into pages of WALINDEX\_PGSZ bytes. Wal-index pages are

\*\* numbered from zero.

\*\*

\*\* If the wal-index is currently smaller the iPage pages then the size

\*\* of the wal-index might be increased, but only if it is safe to do

\*\* so. It is safe to enlarge the wal-index if pWal->writeLock is true

\*\* or pWal->exclusiveMode==WAL\_HEAPMEMORY\_MODE.

\*\*

\*\* Three possible result scenarios:

\*\*

\*\* (1) rc==SQLITE\_OK and \*ppPage==Requested-Wal-Index-Page

\*\* (2) rc>=SQLITE\_ERROR and \*ppPage==NULL

\*\* (3) rc==SQLITE\_OK and \*ppPage==NULL // only if iPage==0

\*\*

\*\* Scenario (3) can only occur when pWal->writeLock is false and iPage==0

\*/

static SQLITE\_NOINLINE int walIndexPageRealloc(

Wal \*pWal, /\* The WAL context \*/

int iPage, /\* The page we seek \*/

volatile u32 \*\*ppPage /\* Write the page pointer here \*/

){

int rc \= SQLITE\_OK;

/\* Enlarge the pWal->apWiData\[\] array if required \*/

if( pWal\->nWiData<=iPage ){

sqlite3\_int64 nByte \= sizeof(u32\*)\*(1+(i64)iPage);

volatile u32 \*\*apNew;

apNew \= (volatile u32 \*\*)sqlite3Realloc((void \*)pWal\->apWiData, nByte);

if( !apNew ){

\*ppPage \= 0;

return SQLITE\_NOMEM\_BKPT;

 }

memset((void\*)&apNew\[pWal\->nWiData\], 0,

sizeof(u32\*)\*(iPage+1\-pWal\->nWiData));

pWal\->apWiData \= apNew;

pWal\->nWiData \= iPage+1;

 }

/\* Request a pointer to the required page from the VFS \*/

assert( pWal\->apWiData\[iPage\]\==0 );

if( pWal\->exclusiveMode\==WAL\_HEAPMEMORY\_MODE ){

pWal\->apWiData\[iPage\] \= (u32 volatile \*)sqlite3MallocZero(WALINDEX\_PGSZ);

if( !pWal\->apWiData\[iPage\] ) rc \= SQLITE\_NOMEM\_BKPT;

 }else{

rc \= sqlite3OsShmMap(pWal\->pDbFd, iPage, WALINDEX\_PGSZ,

pWal\->writeLock, (void volatile \*\*)&pWal\->apWiData\[iPage\]

 );

assert( pWal\->apWiData\[iPage\]!=0

|| rc!=SQLITE\_OK

|| (pWal\->writeLock\==0 && iPage\==0) );

testcase( pWal\->apWiData\[iPage\]\==0 && rc\==SQLITE\_OK );

if( rc\==SQLITE\_OK ){

if( iPage\>0 && sqlite3FaultSim(600) ) rc \= SQLITE\_NOMEM;

 }else if( (rc&0xff)\==SQLITE\_READONLY ){

pWal\->readOnly |= WAL\_SHM\_RDONLY;

if( rc\==SQLITE\_READONLY ){

rc \= SQLITE\_OK;

 }

 }

 }

\*ppPage \= pWal\->apWiData\[iPage\];

assert( iPage\==0 || \*ppPage || rc!=SQLITE\_OK );

return rc;

}

static int walIndexPage(

Wal \*pWal, /\* The WAL context \*/

int iPage, /\* The page we seek \*/

volatile u32 \*\*ppPage /\* Write the page pointer here \*/

){

SEH\_INJECT\_FAULT;

if( pWal\->nWiData<=iPage || (\*ppPage \= pWal\->apWiData\[iPage\])\==0 ){

return walIndexPageRealloc(pWal, iPage, ppPage);

 }

return SQLITE\_OK;

}

/\*

\*\* Return a pointer to the WalCkptInfo structure in the wal-index.

\*/

static volatile WalCkptInfo \*walCkptInfo(Wal \*pWal){

assert( pWal\->nWiData\>0 && pWal\->apWiData\[0\] );

SEH\_INJECT\_FAULT;

return (volatile WalCkptInfo\*)&(pWal\->apWiData\[0\]\[sizeof(WalIndexHdr)/2\]);

}

/\*

\*\* Return a pointer to the WalIndexHdr structure in the wal-index.

\*/

static volatile WalIndexHdr \*walIndexHdr(Wal \*pWal){

assert( pWal\->nWiData\>0 && pWal\->apWiData\[0\] );

SEH\_INJECT\_FAULT;

return (volatile WalIndexHdr\*)pWal\->apWiData\[0\];

}

/\*

\*\* The argument to this macro must be of type u32\. On a little-endian

\*\* architecture, it returns the u32 value that results from interpreting

\*\* the 4 bytes as a big-endian value. On a big-endian architecture, it

\*\* returns the value that would be produced by interpreting the 4 bytes

\*\* of the input value as a little-endian integer.

\*/

#define BYTESWAP32(x) ( \\

 (((x)&0x000000FF)<<24) + (((x)&0x0000FF00)<<8) \\

 \+ (((x)&0x00FF0000)>>8) + (((x)&0xFF000000)>>24) \\

)

/\*

\*\* Generate or extend an 8 byte checksum based on the data in

\*\* array aByte\[\] and the initial values of aIn\[0\] and aIn\[1\] (or

\*\* initial values of 0 and 0 if aIn==NULL).

\*\*

\*\* The checksum is written back into aOut\[\] before returning.

\*\*

\*\* nByte must be a positive multiple of 8.

\*/

static void walChecksumBytes(

int nativeCksum, /\* True for native byte-order, false for non-native \*/

u8 \*a, /\* Content to be checksummed \*/

int nByte, /\* Bytes of content in a\[\]. Must be a multiple of 8\. \*/

const u32 \*aIn, /\* Initial checksum value input \*/

u32 \*aOut /\* OUT: Final checksum value output \*/

){

u32 s1, s2;

u32 \*aData \= (u32 \*)a;

u32 \*aEnd \= (u32 \*)&a\[nByte\];

if( aIn ){

s1 \= aIn\[0\];

s2 \= aIn\[1\];

 }else{

s1 \= s2 \= 0;

 }

/\* nByte is a multiple of 8 between 8 and 65536 \*/

assert( nByte\>=8 && (nByte&7)\==0 && nByte<=65536 );

if( !nativeCksum ){

do {

s1 += BYTESWAP32(aData\[0\]) + s2;

s2 += BYTESWAP32(aData\[1\]) + s1;

aData += 2;

 }while( aData<aEnd );

 }else if( nByte%64\==0 ){

do {

s1 += \*aData++ + s2;

s2 += \*aData++ + s1;

s1 += \*aData++ + s2;

s2 += \*aData++ + s1;

s1 += \*aData++ + s2;

s2 += \*aData++ + s1;

s1 += \*aData++ + s2;

s2 += \*aData++ + s1;

s1 += \*aData++ + s2;

s2 += \*aData++ + s1;

s1 += \*aData++ + s2;

s2 += \*aData++ + s1;

s1 += \*aData++ + s2;

s2 += \*aData++ + s1;

s1 += \*aData++ + s2;

s2 += \*aData++ + s1;

 }while( aData<aEnd );

 }else{

do {

s1 += \*aData++ + s2;

s2 += \*aData++ + s1;

 }while( aData<aEnd );

 }

assert( aData\==aEnd );

aOut\[0\] \= s1;

aOut\[1\] \= s2;

}

/\*

\*\* If there is the possibility of concurrent access to the SHM file

\*\* from multiple threads and/or processes, then do a memory barrier.

\*/

static void walShmBarrier(Wal \*pWal){

if( pWal\->exclusiveMode!=WAL\_HEAPMEMORY\_MODE ){

sqlite3OsShmBarrier(pWal\->pDbFd);

 }

}

/\*

\*\* Add the SQLITE\_NO\_TSAN as part of the return-type of a function

\*\* definition as a hint that the function contains constructs that

\*\* might give false-positive TSAN warnings.

\*\*

\*\* See tag-20200519-1.

\*/

#if defined(\_\_clang\_\_) && !defined(SQLITE\_NO\_TSAN)

\# define SQLITE\_NO\_TSAN \_\_attribute\_\_((no\_sanitize\_thread))

#else

\# define SQLITE\_NO\_TSAN

#endif

/\*

\*\* Write the header information in pWal->hdr into the wal-index.

\*\*

\*\* The checksum on pWal->hdr is updated before it is written.

\*/

static SQLITE\_NO\_TSAN void walIndexWriteHdr(Wal \*pWal){

volatile WalIndexHdr \*aHdr \= walIndexHdr(pWal);

const int nCksum \= offsetof(WalIndexHdr, aCksum);

assert( pWal\->writeLock );

pWal\->hdr.isInit \= 1;

pWal\->hdr.iVersion \= WALINDEX\_MAX\_VERSION;

walChecksumBytes(1, (u8\*)&pWal\->hdr, nCksum, 0, pWal\->hdr.aCksum);

/\* Possible TSAN false-positive. See tag-20200519-1 \*/

memcpy((void\*)&aHdr\[1\], (const void\*)&pWal\->hdr, sizeof(WalIndexHdr));

walShmBarrier(pWal);

memcpy((void\*)&aHdr\[0\], (const void\*)&pWal\->hdr, sizeof(WalIndexHdr));

}

/\*

\*\* This function encodes a single frame header and writes it to a buffer

\*\* supplied by the caller. A frame-header is made up of a series of

\*\* 4-byte big-endian integers, as follows:

\*\*

\*\* 0: Page number.

\*\* 4: For commit records, the size of the database image in pages

\*\* after the commit. For all other records, zero.

\*\* 8: Salt-1 (copied from the wal-header)

\*\* 12: Salt-2 (copied from the wal-header)

\*\* 16: Checksum-1.

\*\* 20: Checksum-2.

\*/

[View remainder of file in raw view](https://github.com/sqlite/sqlite/raw/refs/heads/master/src/wal.c)

## Footer

[ ](https://github.com) © 2026 GitHub, Inc. 

### Footer navigation

* [Terms](https://docs.github.com/site-policy/github-terms/github-terms-of-service)
* [Privacy](https://docs.github.com/site-policy/privacy-policies/github-privacy-statement)
* [Security](https://github.com/security)
* [Status](https://www.githubstatus.com/)
* [Community](https://github.community/)
* [Docs](https://docs.github.com/)
* [Contact](https://support.github.com?tags=dotcom-footer)
* Manage cookies
* Do not share my personal information

You can’t perform that action at this time.