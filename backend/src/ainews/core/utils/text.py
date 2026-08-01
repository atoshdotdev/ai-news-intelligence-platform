from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3", local_files_only=True)


article = """
Iran’s hardliners warn of a ‘coup’ as US truce comes under pressure
By
Mostafa Salem
Officials including Iranian Parliament Speaker Mohammad Bagher Ghalibaf, Chief Justice Gholam-Hossein Mohseni-Eje'i, Iranian President Masoud Pezeshkian, Foreign Minister Abbas Araghchi and IRGC commander general Mohsen Rezaee arrive for a ceremony in Tehran, Iran, on July 3. Morteza Nikoubazl/NurPhoto/Getty Images
As Iran’s President Masoud Pezeshkian walked alongside the coffin of Supreme Leader Ali Khamenei in Tehran last week, some of the black-clad mourners surrounding him chanted not in tribute to the late leader, but directly at him – “death to the compromiser.”

Not far from that site, Abbas Araghchi, Iran’s top diplomat who negotiated a ceasefire with the Trump administration and lifted some sanctions on the Islamic Republic, was forced to flee the funeral after a mob pelted him with rocks amid death chants accusing him of being a “traitorous sellout.”

The hostility directed at top officials during the funeral reflects a theory that has been gaining traction within the Islamic Republic’s most radical factions for months: that Iran’s wartime leaders who negotiated and signed the agreement with Washington are staging a soft coup against the Islamic Republic and its revolutionary ideals while the new supreme leader remains largely invisible for fear of his life – or, as some have suggested, because he is incapacitated.

The hardline factions that attended the funeral in large numbers believe that instead of avenging Khamenei’s killing, Iranian officials have surrendered by signing an agreement that defies the orders of Supreme Leader Mojtaba Khamenei, the late leader’s son and successor. But Khamenei has remained hidden from public view, neither addressing the nation directly nor visibly asserting his authority, even as officials negotiate or govern in his name.
Hardliners have accused Iran’s visible leadership – those running and representing the country as Khamenei remains in hiding – of plotting to consolidate power by suspending parliament, defying his orders in negotiations and attempting to disperse the nightly street rallies that had become a potent power base for fundamentalists.

“Warning to the people of Iran: Is a coup on the way??” Mahmoud Nabavian, an outspoken radical lawmaker, asked on X days before Khamenei’s funeral.

“In these moments of farewell to the martyred Imam (Khamenei), we raise the banner of vengeance for his blood and stand firm against the coup,” he wrote days later.

In Mojtaba’s absence, chief negotiator Mohammad Bagher Ghalibaf, Pezeshkian and Araghchi have become the most visible faces in charge of post-war Iran. Without access to the new supreme leader, hardliners who are unhappy with their performance have instead accused them of plotting a coup, Arash Azizi, a US-based Iran expert and author of the book “What Iranians Want,” told CNN.

“Mojtaba’s continued absence means that they don’t have access to him and also that Ghalibaf and allies are effectively in charge of the country… the ultra-hardliners have thus accused Ghalibaf and Pezeshkian of plotting a ‘coup’ against Mojtaba,” Azizi said.

Mourners chant, fists raised, during a gathering commemorating the late Supreme Leader Ali Khamenei at the Imam Khomeini Mosalla Grand Mosque in Tehran, Iran on July 14.
Mourners chant, fists raised, during a gathering commemorating the late Supreme Leader Ali Khamenei at the Imam Khomeini Mosalla Grand Mosque in Tehran, Iran on July 14. Vahid Salemi/AP
‘Us, the blade and your throat’
Despite widespread calls for wartime unity across Iran, the weeklong grand funeral for Khamenei, killed in late February in Israeli airstrikes coordinated with the United States, became a powerful showcase for the Islamic Republic’s most hardline supporters. They used the occasion to amplify demands to avenge their leader through renewed war with Washington and to declare their rejection of any agreement with Trump.

Their wish now appears to have been fulfilled. A fragile ceasefire between Iran and the US all but collapsed this week after the Revolutionary Guards launched attacks on shipping in the Strait of Hormuz to assert control over the waterway. That prompted retaliatory strikes by Washington and fresh demands by Iranian hardliners to scrap the truce.

Related article
Children wade in the water with cargo ships at anchor in the background and a fisherman nearby, in the Strait of Hormuz off Bandar Abbas, Iran, on  June 30, 2026.
Children wade in the water with cargo ships at anchor in the background and a fisherman nearby, in the Strait of Hormuz off Bandar Abbas, Iran, on June 30, 2026.
Amirhosein Khorgooi/ISNA/AP
The war with Iran has become a battle about a tollbooth. Free seas are at risk

4 min read
In the weeks before hostilities broke out, hardliners turned their fury on the leaders who signed the deal with the US.

“Mr President, if the leader’s conditions are not fulfilled, then it will be us, the blade and your throat,” Mohammad Ali Bakhshi, a security-linked “Maddah” – or religious singer who is loyal to the Iranian regime – warned Pezeshkian during a ceremony. “We will bring hell upon you.”

The open threat to kill the president was widely criticized, but Bakhshi is not known to have faced any legal repercussions.

Other officials under hardline scrutiny include Iran’s chief negotiator with the US, Ghalibaf, a former Revolutionary Guard commander with deep political experience whose credentials enabled him to step up and take charge during the war, emerging as the regime’s de-facto lead operator with broad acceptability.

“They are trying to elevate the role of the Supreme Council for National Security while diminishing the role of the supreme leader and parliament,” Kamran Ghazanfari, a hardline parliamentarian, said in a video statement early July, referring to the council now deciding the country’s most sensitive wartime affairs. “This is the political coup they have designed and are carrying out step by step.”

Iranian parliament members attend a parliament meeting in Tehran on September 28, 2025.
Iranian parliament members attend a parliament meeting in Tehran on September 28, 2025. Majid Asgaripour/Wana News Agency/Reuters
Sidelining the radicals
On Tuesday, Nabavian, the hardline lawmaker who fiercely opposes the agreement and has been one of the leading voices warning of a “coup,” was removed from his position on the parliament’s National Security Commission, along with another parliamentarian critical of the deal.

Nabavian, who was part of Iran’s negotiating delegation before turning against the talks and attempted to derail the agreement by leaking the text to the media before it was signed last month, claimed that Iran’s negotiating team were defying the supreme leader’s red lines in their talks with the US. CNN could not reach Nabavian for comment.

He and others echo the views of “Jebhe-ye Paydari” (the Endurance Front) whose hardline members are often described by observers as “Super Revolutionaries.” They see themselves as the guardians of the values of the 1979 revolution that overthrew the pro-Western monarch and established an Islamic theocracy.

Related article
A man holds a flag with a picture of late leader of the Islamic Revolution Ayatollah Ruhollah Khomeini, late Supreme Leader of Iran Ayatollah Ali Khamenei and Iran's new Supreme Leader Mojtaba Khamenei, during a rally in Tehran, Iran, April 29, 2026.
A man holds a flag with a picture of late leader of the Islamic Revolution Ayatollah Ruhollah Khomeini, late Supreme Leader of Iran Ayatollah Ali Khamenei and Iran's new Supreme Leader Mojtaba Khamenei, during a rally in Tehran, Iran, April 29, 2026.
Majid-Asgaripour/Wana News Agency/Reuters
‘Super Revolutionaries’: The radical Iranian hardliners bent on sabotaging a deal with the US

7 min read
Experts say Iran’s visible leaders are actively trying to marginalize them.

“We’re seeing Ghalibaf exerting influence to sideline these hardline elements,” Hamidreza Azizi, a visiting fellow at the German Institute for International and Security Affairs, told CNN. “They are too costly for the system and they’re bringing their rivalries out in the open especially as the situation in Iran becomes unstable.”

Their numbers are small, but they hold influential positions across the country, including in parliament and at the national broadcaster IRIB, which launched its own campaigns against the president.

It’s unclear how much support the group commands, but one of its most prominent figures – former national security chief Saeed Jalili – garnered more than 13 million votes in the 2024 elections, finishing second. Iran’s population is around 93 million.

Over the months of war and diplomacy with Iran, Trump has repeatedly described the Islamic Republic as “seriously fractured,” arguing that internal divisions have hindered any agreement. Yet despite the visible splits between the new leaders and the hardliners, observers say the regime remains unified around a core objective of ending the war on terms that deliver sanctions relief and preserve Tehran’s control over the Strait of Hormuz.

Still, Khamenei’s continued absence, his conditional support for the truce, the growing empowerment of the Revolutionary Guards, and the massive attendance at his father’s funeral have emboldened hardliners who instead are now pushing their own aggressive agenda to continue the war with the US and Israel.

“My suggestion is that we go to one of the US bases in the region, where there are hundreds, maybe thousands of these American terrorists,” former Iranian foreign minister and hardline figure Manouchehr Mottaki said in a televised interview on Wednesday. “It would be enough if we take 100 soldiers and bring them back to Iran.”
"""


def split_article(text: str, chunk_size: int = 512, chunk_overlap: int = 50):
    splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.split_text(text)


chunks = split_article(article)


print(f"Number of chunks: {len(chunks)}\n")

for i, chunk in enumerate(chunks):
    token_count = len(tokenizer.encode(chunk, add_special_tokens=False))

    print("=" * 80)
    print(f"CHUNK {i + 1} ({token_count} tokens)")
    print("=" * 80)
    print(chunk)
    print()
